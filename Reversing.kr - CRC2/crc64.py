from __future__ import print_function

# Portions Copyright (c) 1996-2001, PostgreSQL Global Development Group
# (Any use permitted, subject to terms of PostgreSQL license; see.)

# If we have a 64-bit integer type, then a 64-bit CRC looks just like the
# usual sort of implementation. (See Ross Williams' excellent introduction
# A PAINLESS GUIDE TO CRC ERROR DETECTION ALGORITHMS, available from
# ftp://ftp.rocksoft.com/papers/crc_v3.txt or several other net sites.)
# If we have no working 64-bit type, then fake it with two 32-bit registers.
#
# The present implementation is a normal (not "reflected", in Williams'
# terms) 64-bit CRC, using initial all-ones register contents and a final
# bit inversion. The chosen polynomial is borrowed from the DLT1 spec
# (ECMA-182, available from http://www.ecma.ch/ecma1/STAND/ECMA-182.HTM):
#
# x^64 + x^62 + x^57 + x^55 + x^54 + x^53 + x^52 + x^47 + x^46 + x^45 +
# x^40 + x^39 + x^38 + x^37 + x^35 + x^33 + x^32 + x^31 + x^29 + x^27 +
# x^24 + x^23 + x^22 + x^21 + x^19 + x^17 + x^13 + x^12 + x^10 + x^9 +

crc_table = [
    0x0000000000000000, 0xB1AA069AF3404101, 0x7A66F79FC2063341, 0xCBCCF10531467240, 0xF4CDEF3F840C6682, 0x4567E9A5774C2783, 0x8EAB18A0460A55C3, 0x3F011E3AB54A14C2, 0xF0A924D52C9E7C47, 0x4103224FDFDE3D46, 0x8ACFD34AEE984F06, 0x3B65D5D01DD80E07, 0x0464CBEAA8921AC5, 0xB5CECD705BD25BC4, 0x7E023C756A942984, 0xCFA83AEF99D46885, 0xF860B3007DBA49CD, 0x49CAB59A8EFA08CC, 0x8206449FBFBC7A8C, 0x33AC42054CFC3B8D, 0x0CAD5C3FF9B62F4F, 0xBD075AA50AF66E4E, 0x76CBABA03BB01C0E, 0xC761AD3AC8F05D0F, 0x08C997D55124358A, 0xB963914FA264748B, 0x72AF604A932206CB, 0xC30566D0606247CA, 0xFC0478EAD5285308, 0x4DAE7E7026681209, 0x86628F75172E6049, 0x37C889EFE46E2148, 0xE9F39CAADFF222D9, 0x58599A302CB263D8, 0x93956B351DF41198, 0x223F6DAFEEB45099, 0x1D3E73955BFE445B, 0xAC94750FA8BE055A, 0x6758840A99F8771A, 0xD6F282906AB8361B, 0x195AB87FF36C5E9E, 0xA8F0BEE5002C1F9F, 0x633C4FE0316A6DDF, 0xD296497AC22A2CDE, 0xED9757407760381C, 0x5C3D51DA8420791D, 0x97F1A0DFB5660B5D, 0x265BA64546264A5C, 0x11932FAAA2486B14, 0xA039293051082A15, 0x6BF5D835604E5855, 0xDA5FDEAF930E1954, 0xE55EC09526440D96, 0x54F4C60FD5044C97, 0x9F38370AE4423ED7, 0x2E92319017027FD6, 0xE13A0B7F8ED61753, 0x50900DE57D965652, 0x9B5CFCE04CD02412, 0x2AF6FA7ABF906513, 0x15F7E4400ADA71D1, 0xA45DE2DAF99A30D0, 0x6F9113DFC8DC4290, 0xDE3B15453B9C0391, 0xCAD5C3FF9B62F4F1, 0x7B7FC5656822B5F0, 0xB0B334605964C7B0, 0x011932FAAA2486B1, 0x3E182CC01F6E9273, 0x8FB22A5AEC2ED372, 0x447EDB5FDD68A132, 0xF5D4DDC52E28E033, 0x3A7CE72AB7FC88B6, 0x8BD6E1B044BCC9B7, 0x401A10B575FABBF7, 0xF1B0162F86BAFAF6, 0xCEB1081533F0EE34, 0x7F1B0E8FC0B0AF35, 0xB4D7FF8AF1F6DD75, 0x057DF91002B69C74, 0x32B570FFE6D8BD3C, 0x831F76651598FC3D, 0x48D3876024DE8E7D, 0xF97981FAD79ECF7C, 0xC6789FC062D4DBBE, 0x77D2995A91949ABF, 0xBC1E685FA0D2E8FF, 0x0DB46EC55392A9FE, 0xC21C542ACA46C17B, 0x73B652B03906807A, 0xB87AA3B50840F23A, 0x09D0A52FFB00B33B, 0x36D1BB154E4AA7F9, 0x877BBD8FBD0AE6F8, 0x4CB74C8A8C4C94B8, 0xFD1D4A107F0CD5B9, 0x23265F554490D628, 0x928C59CFB7D09729, 0x5940A8CA8696E569, 0xE8EAAE5075D6A468, 0xD7EBB06AC09CB0AA, 0x6641B6F033DCF1AB, 0xAD8D47F5029A83EB, 0x1C27416FF1DAC2EA, 0xD38F7B80680EAA6F, 0x62257D1A9B4EEB6E, 0xA9E98C1FAA08992E, 0x18438A855948D82F, 0x274294BFEC02CCED, 0x96E892251F428DEC, 0x5D2463202E04FFAC, 0xEC8E65BADD44BEAD, 0xDB46EC55392A9FE5, 0x6AECEACFCA6ADEE4, 0xA1201BCAFB2CACA4, 0x108A1D50086CEDA5, 0x2F8B036ABD26F967, 0x9E2105F04E66B866, 0x55EDF4F57F20CA26, 0xE447F26F8C608B27, 0x2BEFC88015B4E3A2, 0x9A45CE1AE6F4A2A3, 0x51893F1FD7B2D0E3, 0xE023398524F291E2, 0xDF2227BF91B88520, 0x6E88212562F8C421, 0xA544D02053BEB661, 0x14EED6BAA0FEF760, 0x8C997D55124358A1, 0x3D337BCFE10319A0, 0xF6FF8ACAD0456BE0, 0x47558C5023052AE1, 0x7854926A964F3E23, 0xC9FE94F0650F7F22, 0x023265F554490D62, 0xB398636FA7094C63, 0x7C3059803EDD24E6, 0xCD9A5F1ACD9D65E7, 0x0656AE1FFCDB17A7, 0xB7FCA8850F9B56A6, 0x88FDB6BFBAD14264, 0x3957B02549910365, 0xF29B412078D77125, 0x433147BA8B973024, 0x74F9CE556FF9116C, 0xC553C8CF9CB9506D, 0x0E9F39CAADFF222D, 0xBF353F505EBF632C, 0x8034216AEBF577EE, 0x319E27F018B536EF, 0xFA52D6F529F344AF, 0x4BF8D06FDAB305AE, 0x8450EA8043676D2B, 0x35FAEC1AB0272C2A, 0xFE361D1F81615E6A, 0x4F9C1B8572211F6B, 0x709D05BFC76B0BA9, 0xC1370325342B4AA8, 0x0AFBF220056D38E8, 0xBB51F4BAF62D79E9, 0x656AE1FFCDB17A78, 0xD4C0E7653EF13B79, 0x1F0C16600FB74939, 0xAEA610FAFCF70838, 0x91A70EC049BD1CFA, 0x200D085ABAFD5DFB, 0xEBC1F95F8BBB2FBB, 0x5A6BFFC578FB6EBA, 0x95C3C52AE12F063F, 0x2469C3B0126F473E, 0xEFA532B52329357E, 0x5E0F342FD069747F, 0x610E2A15652360BD, 0xD0A42C8F966321BC, 0x1B68DD8AA72553FC, 0xAAC2DB10546512FD, 0x9D0A52FFB00B33B5, 0x2CA05465434B72B4, 0xE76CA560720D00F4, 0x56C6A3FA814D41F5, 0x69C7BDC034075537, 0xD86DBB5AC7471436, 0x13A14A5FF6016676, 0xA20B4CC505412777, 0x6DA3762A9C954FF2, 0xDC0970B06FD50EF3, 0x17C581B55E937CB3, 0xA66F872FADD33DB2, 0x996E991518992970, 0x28C49F8FEBD96871, 0xE3086E8ADA9F1A31, 0x52A2681029DF5B30, 0x464CBEAA8921AC50, 0xF7E6B8307A61ED51, 0x3C2A49354B279F11, 0x8D804FAFB867DE10, 0xB28151950D2DCAD2, 0x032B570FFE6D8BD3, 0xC8E7A60ACF2BF993, 0x794DA0903C6BB892, 0xB6E59A7FA5BFD017, 0x074F9CE556FF9116, 0xCC836DE067B9E356, 0x7D296B7A94F9A257, 0x4228754021B3B695, 0xF38273DAD2F3F794, 0x384E82DFE3B585D4, 0x89E4844510F5C4D5, 0xBE2C0DAAF49BE59D, 0x0F860B3007DBA49C, 0xC44AFA35369DD6DC, 0x75E0FCAFC5DD97DD, 0x4AE1E2957097831F, 0xFB4BE40F83D7C21E, 0x3087150AB291B05E, 0x812D139041D1F15F, 0x4E85297FD80599DA, 0xFF2F2FE52B45D8DB, 0x34E3DEE01A03AA9B, 0x8549D87AE943EB9A, 0xBA48C6405C09FF58, 0x0BE2C0DAAF49BE59, 0xC02E31DF9E0FCC19, 0x718437456D4F8D18, 0xAFBF220056D38E89, 0x1E15249AA593CF88, 0xD5D9D59F94D5BDC8, 0x6473D3056795FCC9, 0x5B72CD3FD2DFE80B, 0xEAD8CBA5219FA90A, 0x21143AA010D9DB4A, 0x90BE3C3AE3999A4B, 0x5F1606D57A4DF2CE, 0xEEBC004F890DB3CF, 0x2570F14AB84BC18F, 0x94DAF7D04B0B808E, 0xABDBE9EAFE41944C, 0x1A71EF700D01D54D, 0xD1BD1E753C47A70D, 0x601718EFCF07E60C, 0x57DF91002B69C744, 0xE675979AD8298645, 0x2DB9669FE96FF405, 0x9C1360051A2FB504, 0xA3127E3FAF65A1C6, 0x12B878A55C25E0C7, 0xD97489A06D639287, 0x68DE8F3A9E23D386, 0xA776B5D507F7BB03, 0x16DCB34FF4B7FA02, 0xDD10424AC5F18842, 0x6CBA44D036B1C943, 0x53BB5AEA83FBDD81, 0xE2115C7070BB9C80, 0x29DDAD7541FDEEC0, 0x9877ABEFB2BDAFC1] 

class CRC64(object):

    def __init__(self):
        self.crc = 0x0

    def append(self, buffer):
        for c in buffer:
            tab_index = ((self.crc) ^ ord(c)) & 0xFF
            self.crc = crc_table[tab_index] ^ ((self.crc >> 8) & 0xffffffffffffffff)

    def fini(self):
        return self.crc ^0L 


def crc64(buffer):
    crc = CRC64()
    crc.append(buffer)
    
    return crc.fini()
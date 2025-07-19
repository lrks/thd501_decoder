from gnuradio import gr
import pmt
import json

class blk(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="THD501 Decoder",
            in_sig=[],
            out_sig=[])
        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_pdu)

    def parse_data(self, data):
        humid_digit10 = data[2] >> 4
        humid_digit1  = data[2] & 0xf
        humid = humid_digit10*10 + humid_digit1 if (0 <= humid_digit10 <= 9) and (0 <= humid_digit1 <= 9) else None
        temp_digit10 = data[4] & 0xf
        temp_digit1  = data[5] >> 4
        temp_frac1   = data[5] & 0xf
        temp_sign    = -1 if data[3] & 0x8 else 1
        temp = temp_sign * (temp_digit10*10 + temp_digit1 + temp_frac1/10.0) if (0 <= temp_digit10 <= 9) and (0 <= temp_digit1 <= 9) and (0 <= temp_frac1 <= 9) else None
        absolute_humid = None
        if (temp is not None) and (humid is not None):
            e = 6.11 * 10**((7.5*temp)/(237.3+temp))
            ep = e * humid/100.0
            absolute_humid = (217 * ep) / (273.15 + temp)
        return {'temperature': temp, 'humidity':humid, 'absolute_humidity': absolute_humid}

    def save(self, data):
        # debug print
        print("THD501Decoder " + json.dumps(data))

    def handle_pdu(self, pdu):
        EXPECT_PREAMBLE = b'\xd2\x2b'
        meta = pmt.car(pdu)
        data = pmt.cdr(pdu)
        bits = pmt.u8vector_elements(data)
        if len(bits) != 112: return
        payload = int(''.join(map(str, bits)), 2).to_bytes(len(bits)//8, byteorder='big')
        data0 = payload[2:8]
        data0_inv = bytes(x ^ 0xFF for x in data0)
        data1 = payload[8:14]
        self.save({
            'raw'    : payload.hex(),
            'isValid': (EXPECT_PREAMBLE == payload[0:2]) and (data0_inv == data1),
            'data0'  : self.parse_data(data0_inv),
            'data1'  : self.parse_data(data1),
        })
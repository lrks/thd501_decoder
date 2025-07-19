#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: THD501 Decoder
# GNU Radio version: 3.10.12.0

from gnuradio import analog
import math
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time
import satellites.hier
import thd501_decoder_release_epy_block_0 as epy_block_0  # embedded python block
import threading




class thd501_decoder_release(gr.top_block):

    def __init__(self, base_samp_rate=240e3, down_samp_rate=24e3, offset_tuning_freq=0, ppm_correction=0, rrc_filter_coe=10, samp_bw=2.5e3):
        gr.top_block.__init__(self, "THD501 Decoder", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Parameters
        ##################################################
        self.base_samp_rate = base_samp_rate
        self.down_samp_rate = down_samp_rate
        self.offset_tuning_freq = offset_tuning_freq
        self.ppm_correction = ppm_correction
        self.rrc_filter_coe = rrc_filter_coe
        self.samp_bw = samp_bw

        ##################################################
        # Variables
        ##################################################
        self.symbol_time = symbol_time = 2000e-6
        self.timing_ted_gain = timing_ted_gain = 0.1
        self.timing_loop_bw = timing_loop_bw = 0.1
        self.freq = freq = 426.025e6
        self.deviation = deviation = 1000
        self.baud_rate = baud_rate = 1 / symbol_time

        ##################################################
        # Blocks
        ##################################################

        self.satellites_sync_to_pdu_0 = satellites.hier.sync_to_pdu(
            packlen=112,
            sync="01010101010101010101010101010101",
            threshold=0,
        )
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ''
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(base_samp_rate)
        self.rtlsdr_source_0.set_center_freq((freq + offset_tuning_freq), 0)
        self.rtlsdr_source_0.set_freq_corr(ppm_correction, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(2, 0)
        self.rtlsdr_source_0.set_gain_mode(True, 0)
        self.rtlsdr_source_0.set_gain(20, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(samp_bw, 0)
        self.root_raised_cosine_filter_0 = filter.fir_filter_fff(
            1,
            firdes.root_raised_cosine(
                1,
                down_samp_rate,
                (baud_rate*2),
                0.35,
                (int((down_samp_rate / baud_rate) * rrc_filter_coe))))
        self.freq_xlating_fir_filter_xxx_0_0_0 = filter.freq_xlating_fir_filter_ccc((round(base_samp_rate / down_samp_rate)), firdes.low_pass(1.0, down_samp_rate, 2*deviation, 2*deviation), (deviation - offset_tuning_freq), base_samp_rate)
        self.epy_block_0 = epy_block_0.blk()
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(
            digital.TED_EARLY_LATE,
            (down_samp_rate / baud_rate),
            timing_loop_bw,
            1.0,
            timing_ted_gain,
            1.5,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.analog_quadrature_demod_cf_1 = analog.quadrature_demod_cf((down_samp_rate / (2*math.pi*deviation)))


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.satellites_sync_to_pdu_0, 'out'), (self.epy_block_0, 'in'))
        self.connect((self.analog_quadrature_demod_cf_1, 0), (self.root_raised_cosine_filter_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.satellites_sync_to_pdu_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_0_0, 0), (self.analog_quadrature_demod_cf_1, 0))
        self.connect((self.root_raised_cosine_filter_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.freq_xlating_fir_filter_xxx_0_0_0, 0))


    def get_base_samp_rate(self):
        return self.base_samp_rate

    def set_base_samp_rate(self, base_samp_rate):
        self.base_samp_rate = base_samp_rate
        self.rtlsdr_source_0.set_sample_rate(self.base_samp_rate)

    def get_down_samp_rate(self):
        return self.down_samp_rate

    def set_down_samp_rate(self, down_samp_rate):
        self.down_samp_rate = down_samp_rate
        self.analog_quadrature_demod_cf_1.set_gain((self.down_samp_rate / (2*math.pi*self.deviation)))
        self.digital_symbol_sync_xx_0.set_sps((self.down_samp_rate / self.baud_rate))
        self.freq_xlating_fir_filter_xxx_0_0_0.set_taps(firdes.low_pass(1.0, self.down_samp_rate, 2*self.deviation, 2*self.deviation))
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(1, self.down_samp_rate, (self.baud_rate*2), 0.35, (int((self.down_samp_rate / self.baud_rate) * self.rrc_filter_coe))))

    def get_offset_tuning_freq(self):
        return self.offset_tuning_freq

    def set_offset_tuning_freq(self, offset_tuning_freq):
        self.offset_tuning_freq = offset_tuning_freq
        self.freq_xlating_fir_filter_xxx_0_0_0.set_center_freq((self.deviation - self.offset_tuning_freq))
        self.rtlsdr_source_0.set_center_freq((self.freq + self.offset_tuning_freq), 0)

    def get_ppm_correction(self):
        return self.ppm_correction

    def set_ppm_correction(self, ppm_correction):
        self.ppm_correction = ppm_correction
        self.rtlsdr_source_0.set_freq_corr(self.ppm_correction, 0)

    def get_rrc_filter_coe(self):
        return self.rrc_filter_coe

    def set_rrc_filter_coe(self, rrc_filter_coe):
        self.rrc_filter_coe = rrc_filter_coe
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(1, self.down_samp_rate, (self.baud_rate*2), 0.35, (int((self.down_samp_rate / self.baud_rate) * self.rrc_filter_coe))))

    def get_samp_bw(self):
        return self.samp_bw

    def set_samp_bw(self, samp_bw):
        self.samp_bw = samp_bw
        self.rtlsdr_source_0.set_bandwidth(self.samp_bw, 0)

    def get_symbol_time(self):
        return self.symbol_time

    def set_symbol_time(self, symbol_time):
        self.symbol_time = symbol_time
        self.set_baud_rate(1 / self.symbol_time)

    def get_timing_ted_gain(self):
        return self.timing_ted_gain

    def set_timing_ted_gain(self, timing_ted_gain):
        self.timing_ted_gain = timing_ted_gain
        self.digital_symbol_sync_xx_0.set_ted_gain(self.timing_ted_gain)

    def get_timing_loop_bw(self):
        return self.timing_loop_bw

    def set_timing_loop_bw(self, timing_loop_bw):
        self.timing_loop_bw = timing_loop_bw
        self.digital_symbol_sync_xx_0.set_loop_bandwidth(self.timing_loop_bw)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.rtlsdr_source_0.set_center_freq((self.freq + self.offset_tuning_freq), 0)

    def get_deviation(self):
        return self.deviation

    def set_deviation(self, deviation):
        self.deviation = deviation
        self.analog_quadrature_demod_cf_1.set_gain((self.down_samp_rate / (2*math.pi*self.deviation)))
        self.freq_xlating_fir_filter_xxx_0_0_0.set_taps(firdes.low_pass(1.0, self.down_samp_rate, 2*self.deviation, 2*self.deviation))
        self.freq_xlating_fir_filter_xxx_0_0_0.set_center_freq((self.deviation - self.offset_tuning_freq))

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.digital_symbol_sync_xx_0.set_sps((self.down_samp_rate / self.baud_rate))
        self.root_raised_cosine_filter_0.set_taps(firdes.root_raised_cosine(1, self.down_samp_rate, (self.baud_rate*2), 0.35, (int((self.down_samp_rate / self.baud_rate) * self.rrc_filter_coe))))



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--base-samp-rate", dest="base_samp_rate", type=eng_float, default=eng_notation.num_to_str(float(240e3)),
        help="Set capture sample rate [default=%(default)r]")
    parser.add_argument(
        "--down-samp-rate", dest="down_samp_rate", type=eng_float, default=eng_notation.num_to_str(float(24e3)),
        help="Set down sampling rate [default=%(default)r]")
    parser.add_argument(
        "--offset-tuning-freq", dest="offset_tuning_freq", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set offset tuning frequency [default=%(default)r]")
    parser.add_argument(
        "--ppm-correction", dest="ppm_correction", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set frequency correction (ppm) [default=%(default)r]")
    parser.add_argument(
        "--rrc-filter-coe", dest="rrc_filter_coe", type=eng_float, default=eng_notation.num_to_str(float(10)),
        help="Set rrc filter coe [default=%(default)r]")
    parser.add_argument(
        "--samp-bw", dest="samp_bw", type=eng_float, default=eng_notation.num_to_str(float(2.5e3)),
        help="Set capture bandwidth [default=%(default)r]")
    return parser


def main(top_block_cls=thd501_decoder_release, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(base_samp_rate=options.base_samp_rate, down_samp_rate=options.down_samp_rate, offset_tuning_freq=options.offset_tuning_freq, ppm_correction=options.ppm_correction, rrc_filter_coe=options.rrc_filter_coe, samp_bw=options.samp_bw)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    tb.wait()


if __name__ == '__main__':
    main()

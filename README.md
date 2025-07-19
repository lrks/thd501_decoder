# thd501_decoder
「シチズン (CITIZEN) コードレス温湿度計 THD501」の無線信号をデコードするプログラムです。
受信デバイスはRTL-SDRドングルを前提としています。

詳細: https://telecotele.com/projects/ （記事作成中）

## ディレクトリ/ファイルの説明
```
.
├── debug
│   ├── RTL-SDR-1MSps-1MHz_266C_86%.complex # 温度26.6C、湿度86%の信号
│   ├── RTL-SDR-1MSps-1MHz_279C_HI%.complex # 温度27.9C、湿度HI（測定範囲外）の信号
│   ├── run.log                  # デコード用Pythonスクリプトを動かした際のstdout
│   └── thd501_decoder_debug.grc # デコーダのGRC（開発用）
├── thd501_decoder_release.grc   # デコーダのGRC（本番用）
├── thd501_decoder_release.py    # デコーダのGRC（本番用）から作成されたPythonスクリプト
└── thd501_decoder_release_epy_block_0.py # Embedded Python Blockの中身。thd501_decoder_release.py内部から呼ばれる
```

## 実行例
```
$ python3 thd501_decoder_release.py --help
usage: thd501_decoder_release.py [-h] [--base-samp-rate BASE_SAMP_RATE] [--down-samp-rate DOWN_SAMP_RATE]
                                 [--offset-tuning-freq OFFSET_TUNING_FREQ] [--ppm-correction PPM_CORRECTION]
                                 [--rrc-filter-coe RRC_FILTER_COE] [--samp-bw SAMP_BW]

options:
  -h, --help            show this help message and exit
  --base-samp-rate BASE_SAMP_RATE
                        Set capture sample rate [default='240.0k']
  --down-samp-rate DOWN_SAMP_RATE
                        Set down sampling rate [default='24.0k']
  --offset-tuning-freq OFFSET_TUNING_FREQ
                        Set offset tuning frequency [default='0.0']
  --ppm-correction PPM_CORRECTION
                        Set frequency correction (ppm) [default='0.0']
  --rrc-filter-coe RRC_FILTER_COE
                        Set rrc filter coe [default='10.0']
  --samp-bw SAMP_BW     Set capture bandwidth [default='2.5k']


$ python3 thd501_decoder_release.py --down-samp-rate 8k --ppm-correction 42 --rrc-filter-coe 1
  :
  :
THD501Decoder {"raw": "d22b2ead9e6c9cecd15261936313", "isValid": true, "data0": {"temperature": 31.3, "humidity": 61, "absolute_humidity": 19.874260292396634}, "data1": {"temperature": 31.3, "humidity": 61, "absolute_humidity": 19.874260292396634}}
  :
THD501Decoder {"raw": "d22b3fad9e6c9cedc05261936312", "isValid": true, "data0": {"temperature": 31.2, "humidity": 61, "absolute_humidity": 19.768142038197404}, "data1": {"temperature": 31.2, "humidity": 61, "absolute_humidity": 19.768142038197404}}
```

* raw ... 生のペイロード(112 bits)の16進数文字列
* isValid ... ペイロードが0xd22b始まりかつdata0の反転データとdata1が一致するか
  * 0xd22bは製品IDの可能性があり、別環境だと常にfalseになってしまう可能性あり
* temperature, humidity ... 受信した値
  * 測定範囲外の場合はnullとなる
* absolute\_humidity ... temperatureとhumidityから計算した容積絶対湿度
  * これもnullになる可能性あり

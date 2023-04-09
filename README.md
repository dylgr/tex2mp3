# tex2mp3

## About

A script to convert `.tex` files to audio format.

Uses Amazon Polly for TTS and OpenAI to convert LaTeX equations to an easier to read format.

## Steps

1. Download the paper source files from `from ArXiv > Download > Other Formats > Source` and extract to the `papers/` directory.
2. Convert the `.tex` file to plaintext with pandoc using the shell script:
```sh
./process.sh papers/1706/ms.tex ./papers/attention.txt  
```
3. Convert the plaintext file to audio via:
```sh
python3 tex2mp3.py -i ./papers/attention.txt -o ./output/attention.mp3 -s ${S3_BUCKET}
```
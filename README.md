# Prerequisites
* Chrome or Firefox
* Python 3.10.6
# Requirements
* `pip install -r requirements.txt`
# Parse reactions
`python parse.py --pages <pages> --url-template <url_template> --browser <browser> --headless`

Params:
* pages — pages to parse.
Examples: `1-100`,`1,2,3`,`1`,`1,2-5,7-9`.
* url-template — url with search results.
Examples: `https://scifinder-n.cas.org/search/reaction/6388a3a2d84c685d487d2c38/{page}`.
* browser — browser to use.
Examples: `chrome`, `firefox`.
* headless — flag that controls the launch of the browser in the background.

# Parse SMILES
`python parse_smiles.py <input_filepath> <output_filepath>`

Params:
* input_filepath — path to an input file.
Examples: `input.csv`.
* output_filepath — path to an output file.
Examples: `output.csv`.

* Input file example:
```
query
Water
74-85-1
```
* Output file example:
```
query,result
Water,Multiple results
74-85-1,C=C
```
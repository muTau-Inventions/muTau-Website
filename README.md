# muTau-Website
Our company website

# How to use
## Deploy
``` bash
git clone  https://github.com/muTau-Inventions/muTau-Website.git
cd muTau-Website
make build
make up
```
## docs
For documentation, create a docs directory where you put your entire documentation in the form of .md files. The .md files will be automatically rendered on the website.
## research
To use the research function of the website, create a directory called research where you place your papers in the following structure:
```
.research
├── test
│   ├── information.json
│   └── paper.pdf
└── 2test
    ├── information.json
    └── paper.pdf
```
As you can see, for every research paper you create a subfolder. In each subfolder, you must include your research paper named paper.pdf (any other file name will not work).
You must also include an information.json file in every subfolder with the following format:
``` json
{
  "title": "Example",
  "authors": "Max Mustermann",
  "date": "2026-02-11",
  "description": "abstract of the paper"
}
```
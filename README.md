Marksy Convert
==============

Sublime Text plugin that uses [Marksy API](http://marksy.arc90.com/) to convert between markup languages

## Installation

### Package Control
The preferred method of installation is via Sublime Package Control.

Install via Sublime Package Control

- From inside Sublime Text, open Package Control's Command Pallet: super + shift + p.
- Type install package and press Return. A list of available packages will be displayed.
- Type Marksy Convert and press Return. The package will be downloaded to the appropriate directory.

### Manual Installation

Create a directory called Marksy Convert in the Sublime Text Packages directory for your platform
Download or clone [this repository](https://github.com/thomscode/Marksy-Convert) to the directory you just created.

## Usage:
- Create a new file and type some markup, or open a markup file.
- Open the Command Pallet: super + shift + p
- Type Marksy Convert and select the markup language you want to convert your text into.
- The plugin attempts to detect the markup language you are converting from
  - If the detected language is incorrect or not selected, select the proper language
- The text is automatically converted via the Marksy API and opened in a new window.

Is able to convert from:

- Markdown
- Rst
- Textile
- Html
- Mediawiki
- Jira (Confluence)
- Github (GFM)

to:

- Markdown
- Rst
- Textile
- Html
- Mediawiki
- Jira (Confluence)
- Googlecode
- Jspwiki
- Moinmoin
- Trac

-----

Marksy is a product of [Arc90](http://marksy.arc90.com). This plugin is not a product of, directly related to, or supported by Arc90.


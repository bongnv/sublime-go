# sublime-go &middot; [![Build Status](https://travis-ci.org/bongnv/sublime-go.svg?branch=master)](https://travis-ci.org/bongnv/sublime-go)
Al Sublime Text package for working with Go.

## Features
- Code format (using `goimports`)
- Goto definition (using `guru`). Support modified files.
- Linter (using `golint` and `SublimeLinter`)

## Requirements

You probably need to install some golang tools:
```shell
go get -u golang.org/x/tools/cmd/goimports
go get -u github.com/nsf/gocode
go get -u golang.org/x/tools/cmd/guru
go get -u golang.org/x/lint/golint
```

Make sure [`SublimeLinter`](http://www.sublimelinter.com/en/stable/) is installed in order to golint to work properly.

## Configurations

The plugin contributes the following settings:
- `go_enable_default_hot_keys`: Enable default hot keys provided by the package (default: `true`)

## Known Issues

TODO

## Release Notes

See [`CHANGELOG.md`](CHANGELOG.md) file

## For more information

* Some python codes are copied from https://github.com/nsf/gocode/blob/master/subl3

## License
See [`LICENSE`](LICENSE) file

**Enjoy!**

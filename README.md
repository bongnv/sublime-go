# sublime-go &middot; [![Build Status](https://travis-ci.org/bongnv/sublime-go.svg?branch=master)](https://travis-ci.org/bongnv/sublime-go)
A Sublime Text package for working with Go.

## Features
- Code completion (using `gocode`)
- Code format (using `goimports`)
- Goto definition (using `guru`). Support modified files.
- Linter (using `golint`, `go vet`, `megacheck` with `SublimeLinter`)
- Real-time linting (using `gotype-live`)
- Find all references (using `guru`). Support modified files.

## Requirements

You probably need to install some golang tools:
```shell
go get -u golang.org/x/tools/cmd/goimports
go get -u github.com/nsf/gocode
go get -u golang.org/x/tools/cmd/guru
go get -u golang.org/x/lint/golint
go get -u github.com/tylerb/gotype-live
go get -u honnef.co/go/tools/cmd/megacheck
```

Make sure [`SublimeLinter`](http://www.sublimelinter.com/en/stable/) is installed in order to have lint features.

## Configurations

The plugin contributes the following settings:

* `go_override_default_hot_keys`: Override default hot keys to provide functionality from the package (default: `true`)
* To have custom formatter before files saving, add a similar configuration to the following to `.sublime-project` files:
```json
  "golang": {
    "pre_save_formats": {
      "goimports": {
        "cmd": ["gofmt", "-e"]
      }
    }
  }
```

## Known Issues

TODO

## Release Notes

See [`CHANGELOG.md`](CHANGELOG.md) file

## For more information

* I didn't write all of them. Some python codes are copied from https://github.com/nsf/gocode/blob/master/subl3 or https://github.com/golang/sublime-config

## License
See [`LICENSE`](LICENSE) file

**Enjoy!**

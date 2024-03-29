radialnet
=========

A network visualization tool based on radial layout.


using
=====

Use the following commands to setup your local copy.

```shell
$ git clone https://github.com/labepi/radialnet.git
$ cd radialnet/
$ git submodule update --init --recursive
```

Now you may start the application making it executable or with `python` command.

```shell
$ chmod +x radialnet.pyw
$ ./radialnet.pyw
```

In order to use it, you may execute a Scan using Nmap as a backend tool (initially assumed to be on `/usr/bin/nmap`, but can be changed in config.cfg). You may also use it loading any Nmap XML output file (a sample is included in `share/sample/nmap_example.xml`).

```shell
$ ./radialnet.pyw share/sample/nmap_example.xml
```

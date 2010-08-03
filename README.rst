=====
MuxPD
=====
----------------------------
A simple multiplexer for MPD
----------------------------

Motivation
==========

If you have multiple separate places from which commands to your MPD are dispatched (say, your window manager listens for XF86AudioNext or something) and you switch between locations, that have their own mpd hosted - for instance a hackerspace - it can sometimes be a big hassle to fiddle around with environment variables. Getting these to where you need them is not always easy. Thus, I created MuxPD, which is a very thin intermediate layer that delegates connections to the selected MPD.

Installation
============

First of all, you need to have socat for the forwarding to work at all. You may want to install some mpd client programs and an mpd server, but you do not need to - not only can muxpd be used to delegate remote connections to other MPDs, it can also be used to forward arbitrary TCP-based protocols. It is in no way limited to the MPD protocol.

If you run an MPD locally, you will want to change its port from the default port (6600) to 6601 in /etc/mpd.conf, because muxpd will, by default, listen on 6600. This will cause MPD clients with no configuration set up to connect to MuxPD instead.

Invocation
==========

In order for MPD clients to function, you will need to run an instance of MuxPD all the time. MuxPD can safely be run in the background from an xsession or so, or you can start it at whatever time you want. The first MuxPD instance will handle all connections in the future. New MuxPD calls will delegate the change requests to the already running MuxPD instance, if there is one and it reacts to connections.

Call muxpd without any options and it will set up redirects to localhost:6601. Call muxpd with :port, to let it forward to localhost:port or with hostname:port, which will forward to hostname:port. If you only supply one argument, MuxPD will forward to that as the hostname and 6600 as the port.

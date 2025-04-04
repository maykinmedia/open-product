.. _installation_reference_time:

=================
Dealing with time
=================

Dealing with time is a hard problem - the impression is that time is always incrementing
and consistent, but that's not the case when dealing with networks and computers in
general. Common examples are leap seconds and server or client clock drift.

General recommendations
=======================

In general, we advise to make use of `NTP`_ services for both client and server. If
possible, both client and server should use the *same* services so that their clocks are
in sync.

Where Open Product deals with time-aspects
============================================

Open Product deals with time-based validations in a number of places, of which you can
configure how Open Product deals with them for a subset of these places.

API resource validation
-----------------------

In certain places validation takes places that a date(time) must be in the future
or must be in the past (= may not be in the future). This validation is performed
against the server time.

.. _NTP: https://en.wikipedia.org/wiki/Network_Time_Protocol

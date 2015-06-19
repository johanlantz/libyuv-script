# libyuv-script
Python script for cross compiling libyuv

Usage: python build_libyuv.py -platform [iOS, Android etc]

# iOS
iOS will build armv7, armv7s, arm64 and x86_64 and put them into a fat binary.
For some reason the ia32 option also produces a x86_64 build and the fix for this is pending (no feedback from the Google group so far).

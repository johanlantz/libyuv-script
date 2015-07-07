# libyuv-script
Python script for cross compiling libyuv

Usage: python build_libyuv.py -platform [iOS, Android etc]
Output: The builds for each architecture will be available in the libs folder.

# iOS
iOS will build armv7, armv7s, arm64, i386 and x86_64 and put them into a fat binary located in the libs/xcrun folder.

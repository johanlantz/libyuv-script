###########################################################################
#  Automatic build script for libyuv
#
# Johan, June 2015
###########################################################################
import os
import subprocess
import argparse
import shutil

###########################################################################
#  Helper functions													      #
###########################################################################
def checkSVN():
	try:
	    res = subprocess.Popen(['svn', '--version'],
	                           stderr=subprocess.STDOUT,
	                           stdout=subprocess.PIPE).communicate()[0]
	    print res
	except:
	    print "svn not found. Please install svn in order to be able to checkout pjproject. " + \
	          "\nWin32 users with TortoiseSVN must remember to install command line tools " + \
	          "during the Tortoise installation."
	    quit()

def checkGClient():
    try:
        res = subprocess.Popen(['gclient', '--version'],
                               stderr=subprocess.STDOUT,
                               stdout=subprocess.PIPE).communicate()[0]
        print (res)
    except:
        print("Depot tools not found. ")
	print("Follow instructions in https://sites.google.com/a/chromium.org/dev/developers/how-tos/depottools")
	print("Add export PATH=/my_working_directory/depot_tools:$PATH")
	print("to your ~/.bash_profile and do source ~/.bash_profile to re-initate.")
        quit()


def checkoutLibyuv():
	if os.path.exists("libyuv-read-only"):
		shutil.rmtree("libyuv-read-only")
	print("Checking out libyuv from Google")
	os.system("svn checkout http://libyuv.googlecode.com/svn/trunk/ libyuv-read-only")

###########################################################################################
#  Build functions 																		  #
#  Based on instructions found here: https://code.google.com/p/libyuv/wiki/GettingStarted #
#  Completely fresh builds for each arch to avoid cleaning issues. 						  #
###########################################################################################
def buildForiOS():
	#It is not documented on the Google page but the arm64 build actucally produces a fat binary with armv7, armv7s and arm64 and the x86_64 build builds the i386 as well if subarch is defined
	archList = ["arm64", "x86_64"]
   	if os.path.exists("libs"):
		shutil.rmtree("libs")

	os.makedirs("libs")
	os.makedirs("libs/xcrun")
	
	for arch in archList:
		print("Starting " + arch + " build.")
		targetDir = ""
		#start fresh for each arch
		if os.path.exists("libyuv"):
			shutil.rmtree("libyuv")
		os.remove(".gclient")

		checkoutLibyuv()

		os.system("gclient config https://chromium.googlesource.com/libyuv/libyuv");
		with open('.gclient', 'a') as file:
			file.write("target_os=['ios']")
		os.system("gclient sync")
		os.system("gclient sync --nohooks")
		os.system("gclient sync --nohooks")

		print("Entering libyuv folder.")
		os.chdir("libyuv")
		if (arch == "armv7"):
			targetDir = "out_ios/Release-iphoneos"
			commandLine = "GYP_DEFINES=\"OS=ios target_arch=armv7\" GYP_CROSSCOMPILE=1 GYP_GENERATOR_FLAGS=\"output_dir=out_ios\" ./gyp_libyuv -f ninja --depth=. libyuv.gyp && "
		elif (arch == "arm64"):
			targetDir = "out_ios/Release-iphoneos"
			commandLine = "GYP_DEFINES=\"OS=ios target_arch=armv7 target_subarch=64\" GYP_CROSSCOMPILE=1 GYP_GENERATOR_FLAGS=\"output_dir=out_ios\" ./gyp_libyuv -f ninja --depth=. libyuv.gyp && "
		elif (arch == "x86_64"):
			targetDir = "out_ios/Release-iphonesimulator"
			commandLine = "GYP_DEFINES=\"OS=ios target_arch=x64  target_subarch=32\" GYP_CROSSCOMPILE=1 GYP_GENERATOR_FLAGS=\"output_dir=out_ios\" ./gyp_libyuv -f ninja --depth=. libyuv.gyp && "
		elif (arch == "i386"):
			targetDir = "out_ios/Release-iphonesimulator"
			commandLine = "GYP_DEFINES=\"OS=ios target_arch=ia32  target_subarch=32\" GYP_CROSSCOMPILE=1 GYP_GENERATOR_FLAGS=\"output_dir=out_ios\" ./gyp_libyuv -f ninja --depth=. libyuv.gyp && "
		
		else:
			print("Error: Unsupported architecture " + arch);
			quit()

		commandLine += "ninja -j7 -C " + targetDir
		os.system(commandLine)
		print("Build for " + arch + " completed. Stepping out to working dir.")
		os.chdir("..")

		os.makedirs("libs/" + arch)
		shutil.copy("libyuv/" + targetDir + "/libyuv.a", "libs/" + arch)
		
		if(arch.find("arm") != -1):
			shutil.copy("libyuv/" + targetDir + "/libyuv_neon.a", "libs/" + arch)
		print("Copied " + arch + " libraries to " + "libs/" + arch)

	print("All combinations built. Create fat binaries.")
	xcrunCommandLine = "xcrun -sdk iphoneos lipo"
	for arch in archList:
		xcrunCommandLine += " libs/" + arch + "/libyuv.a"

	xcrunCommandLine += " -create -output libs/xcrun/libyuv.a"
	os.system(xcrunCommandLine)

	neonLibs = ""
	for arch in archList:
		if(arch.find("arm") != -1):
			neonLibs += " libs/" + arch + "/libyuv_neon.a"
	if (neonLibs != ""):
		xcrunCommandLine = "xcrun -sdk iphoneos lipo" + neonLibs + " -create -output libs/xcrun/libyuv_neon.a"
		os.system(xcrunCommandLine)
	else:
		print("No arm builds choosen so no xcrun needed for the neon lib.")

	print("All done. The final binaries can be found in libs/xcrun/")
	print("Currently the i386 version is not built since the ia32 parameter produces x64 builds as well for some reason.")
	
        

###########################################################################
#  Main script 														      #
###########################################################################
checkSVN()
checkGClient()

parser = argparse.ArgumentParser()

parser.add_argument("-platform",
                    help="The OS to build for",
                    choices=['Win32', 'iOS', 'android', 'WP8', 'unix'],
                    required=True)
args = parser.parse_args()

if args.platform == "iOS":
	buildForiOS()
else:
	print("Unsupported platform " + args.platform)

from os import getcwd

TIME_FRAMERATE          = 60

ROM_LOAD_BANNER         = True                  # Nice-to-have. Slows initial launch but extracts the title and banner icon from ROM

NDS_USE_FIRMWARE_MAC    = True                  # Uses MAC address from DS firmware instead of system. Keeps certain cipher checks (Hidden Door) accurate to NDS
                                                #     Results are tied to the MAC address of this device so unless using NDS firmware, ciphers are not portable
NAME_INTERFACE_MAC      = None                  # String representation of the interface used for grabbing the MAC address. Leave as 'None' if default is okay.
                                                #     If you're experiencing very slow cipher generations or odd results, make sure the name given is a valid interface

WINDOW_DEFAULT_NAME     = "widebrim"
WINDOW_SCALE_TO_VIEW    = True                  # For high DPI devices, widebrim will be small at default resolution. Enable this to integer scale where possible

PATH_ROM        = getcwd() + "\\rom2.nds"
PATH_SAVE       = getcwd() + "\\rom2.sav"
PATH_NDS_FIRM   = getcwd() + "\\firmware.bin"   # Path to DS (DSi unsupported) firmware file containing the WiFi configuration data
"""
Suppress common warnings from scapy and other libraries
Import this at the beginning of scripts to clean up output
"""
import warnings
import logging

# Suppress cryptography deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='scapy')
warnings.filterwarnings('ignore', message='.*TripleDES.*')

# Suppress Wireshark manuf warnings
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)

# Suppress all scapy warnings
logging.getLogger('scapy').setLevel(logging.ERROR)

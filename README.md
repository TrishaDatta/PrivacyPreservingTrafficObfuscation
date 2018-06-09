# PrivacyPreservingTrafficObfuscation

This is the code described in "A Developer-Friendly Library for Smart Home IoT Privacy-Preserving Traffic Obfuscation" 
published at IoT S&P'18: ACM SIGCOMM 2018 Workshop on IoT Security and Privacy , August 20, 2018, Budapest, Hungary. 
The paper and an in-depth description of the library can be found here: <link>

This library is meant to be used by IoT developers to obfuscate the traffic sent by their devices. 
By "obfuscation", we meant that attackers should not be able to look at the shape  of traffic
and determine when a user is using the device.

We offer two solutions for different kinds of devices: high-latency devices and low-bandwidth low-latency devices. By high-latency devices, we mean devices whose functionality would not be affected by long delays. By low-bandwidth low-latency devices, we mean devices that do not send out large amounts of data at once and whose functionality would be affected by long delays. The high-latency device solution imposes developer-chosen distributions on the packet sizes and interpacket delays of traffic. The low-bandwidth low-latency device solution enforces a constant rate of traffic by using constant developer-specified packet size and interpacket delay. We imagine that developers may need to experiment with both libraries to see which is best suited to their device.

For our solution to work, both the client and server need to be using the code from our provided libraries. The client side creates a Sender object that is initialized with parameters that customize the solutions for each individual device. The high-latency solution constructor takes in a host and port to connet to, 
The server side simply 



<div style="border: solid black 5px; border-radius: 10px; background-color: #AADDFF; padding-left: 20px; padding-right: 20px;
padding-bottom: 20px;">


    <p>
        <strong>Scan for Snips</strong>
    </p>

    <form>
        <input type="button" id="lan_button" value="Scan 192.168.1.* port 1884" onclick="lan_scan(this.form);" />
        <input type="button" id="lan_button_stop" value="Stop Scan" onclick="lan_stop(this.form);" disabled="disabled"/>
    </form>

    <div id="lan_results" style="padding-top: 10px;"></div>

    <div id="custom_result"></div>

</div>
<h1 id=list>-</h1>

<div id="testdiv" style="visibility: hidden"></div>

<script>
//////////////////////////////////////////////////////
//////////////////////////////////////////////////////
// RTC get IP address
//////////////////////////////////////////////////////
//////////////////////////////////////////////////////

var RTCIPAddress=[];
// NOTE: window.RTCPeerConnection is "not a constructor" in FF22/23
var RTCPeerConnection = /*window.RTCPeerConnection ||*/ window.webkitRTCPeerConnection || window.mozRTCPeerConnection;

if (RTCPeerConnection) (function () {
    var rtc = new RTCPeerConnection({iceServers:[]});
    if (1 || window.mozRTCPeerConnection) {      // FF [and now Chrome!] needs a channel/stream to proceed
        rtc.createDataChannel('', {reliable:false});
    };
    
    rtc.onicecandidate = function (evt) {
        // convert the candidate to SDP so we can run it through our general parser
        // see https://twitter.com/lancestout/status/525796175425720320 for details
        if (evt.candidate) grepSDP("a="+evt.candidate.candidate);
    };
    rtc.createOffer(function (offerDesc) {
        grepSDP(offerDesc.sdp);
        rtc.setLocalDescription(offerDesc);
    }, function (e) { console.warn("offer failed", e); });
    
    
    var addrs = Object.create(null);
    addrs["0.0.0.0"] = false;
    function updateDisplay(newAddr) {
        if (newAddr in addrs) return;
        else addrs[newAddr] = true;
        var displayAddrs = Object.keys(addrs).filter(function (k) { return addrs[k]; });
        RTCIPAddress=displayAddrs;
        document.getElementById('list').textContent = displayAddrs.join(" or perhaps ") || "n/a";
    }
    
    function grepSDP(sdp) {
        var hosts = [];
        sdp.split('\r\n').forEach(function (line) { // c.f. http://tools.ietf.org/html/rfc4566#page-39
            if (~line.indexOf("a=candidate")) {     // http://tools.ietf.org/html/rfc4566#section-5.13
                var parts = line.split(' '),        // http://tools.ietf.org/html/rfc5245#section-15.1
                    addr = parts[4],
                    type = parts[7];
                if (type === 'host') updateDisplay(addr);
            } else if (~line.indexOf("c=")) {       // http://tools.ietf.org/html/rfc4566#section-5.7
                var parts = line.split(' '),
                    addr = parts[2];
                updateDisplay(addr);
            }
        });
    }
})(); else {
    document.getElementById('list').innerHTML = "<code>ifconfig | grep inet | grep -v inet6 | cut -d\" \" -f2 | tail -n1</code>";
    document.getElementById('list').nextSibling.textContent = "In Chrome and Firefox your IP should display automatically, by the power of WebRTCskull.";
}





//////////////////////////////////////////////////////
//////////////////////////////////////////////////////
// SCANNER SCRIPT 
//////////////////////////////////////////////////////
//////////////////////////////////////////////////////


    /* The scanner needs these global variables for an ugly hack. */
    var last_scanobj_index = 0;
    var scanobjs = {};
    function PortScanner(ip, port)
    {
        
        this.ip = ip;
        this.port = port;
        this.on_open_or_closed = null;
        this.on_stealthed = null;
        this.start_time = null;
        this.timed_out = null;
        this.total_time = null;

        this.run = function () {
            /* Check that the client gave us all the callbacks we need. */
            if (this.on_open_or_closed == null) {
                alert("Please set the on_open_or_closed callback!");
            }
            if (this.on_stealthed == null) {
                alert("Please set the on_stealthed callback!");
            }

            /* Save this object in the global directory (UGLY HACK). */
            var our_scanobj_index = last_scanobj_index;
            last_scanobj_index++;
            scanobjs[our_scanobj_index] = this;

            /* Record the starting time. */
            this.start_time = (new Date()).getTime();

            /* Create the div to load the image, passing our object's index into
                the global directory so that it can be retrieved. */
            document.getElementById("testdiv").innerHTML = '<img src="http://' + ip + ':' + port + 
                '" alt="" onerror="error_handler(' + our_scanobj_index + ');" />';

            // XXX: What's the right way to do this in JS?
            var thiss = this;
            setTimeout(
                function () {
                    /* This will be non-null if the event hasn't fired yet. */
                    if (scanobjs[our_scanobj_index]) {
                        scanobjs[our_scanobj_index] = null;
                        thiss.timed_out = true;
                        thiss.on_stealthed();
                    }
                },
                2000 // 10000
            );
        }
    }

    function error_handler(index)
    {
        /* Get the PortScanner object back. */
        var thiss = scanobjs[index];

        /* If it's null, the scan timed out. */
        if (thiss == null) {
            return;
        }
        /* Set it to null so the timeout knows we handled it. */
        scanobjs[index] = null;
        thiss.timed_out = false;

        /* Measure the amount of time it took for the load to fail. */
        thiss.total_time = (new Date()).getTime() - thiss.start_time;

        /* Call the appropriate callback. */
        if (thiss.total_time < 1500) {
            thiss.on_open_or_closed();
        } else {
            thiss.on_stealthed();
        }
    }

    function custom_scan(form)
    {
        var ip = form.custom_ipaddr.value;
        var port = form.custom_port.value;
        var ip_addr_re = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;

        var match = ip_addr_re.exec(ip);
        if ( match == null ) {
            alert("That isn't a valid IPv4 address.");
            return;
        }

        if (match[1] > 255 || match[2] > 255 || match[3] > 255 || match[4] > 255) {
            alert("That isn't a valid IPv4 address.");
        }

        port = parseInt(port);
        if (isNaN(port) || port < 0 || port > 65535) {
            alert("Bad port number");
        }

        document.getElementById("custom_button").disabled = true;
        document.getElementById("custom_result").innerHTML = "Scanning... This will take up to 10 seconds.";

        var scanner = new PortScanner(ip, port);

        scanner.on_stealthed = function () {
            if (scanner.timed_out) {
                document.getElementById("custom_result").innerHTML = "Case 2 (no response after 10s).";
            } else {
                document.getElementById("custom_result").innerHTML = "Case 2 (" + this.total_time + " ms).";
            }
            document.getElementById("custom_button").disabled = false;
        }

        scanner.on_open_or_closed = function () {
            document.getElementById("custom_result").innerHTML = "Case 1 (" + this.total_time + " ms)."
            document.getElementById("custom_button").disabled = false;
        }

        scanner.run();
    }

    /* This variable keeps track of which 192.168.1 IP to scan next. */
    var current_octet;
    var stop;
    function lan_scan(form)
    {
        document.getElementById("lan_button").disabled = true;
        document.getElementById("lan_button_stop").disabled = false;

        /* Skip .1 since it might visibly prompt for a password. */
        current_octet = 2;
         current_octet = 136;
        stop = false;

        var scanner = new PortScanner("192.168.1." + current_octet, 1884);
        scanner.on_stealthed = lan_on_stealthed;
        scanner.on_open_or_closed = lan_on_open_or_closed;
        scanner.run();

        document.getElementById("lan_results").innerHTML = "Scanning... <br />";
    }

    function lan_stop(form)
    {
        stop = true;
        document.getElementById("lan_button").disabled = false;
        document.getElementById("lan_button_stop").disabled = true;
    }

    function lan_on_stealthed()
    {
        var res_div = document.getElementById("lan_results");
        res_div.innerHTML += "192.168.1." + current_octet + ": ";
        if (this.timed_out) {
            res_div.innerHTML += "Case 2 (no response after 10 seconds). <br />";
        } else {
            res_div.innerHTML += "Case 2 (" + this.total_time + " ms). <br />";
        }

        current_octet += 1;

        if (stop || current_octet >= 255) {
            res_div.innerHTML += "Done. <br />";
            document.getElementById("lan_button").disabled = false;
            document.getElementById("lan_button_stop").disabled = true;
            return;
        }

        var scanner = new PortScanner("192.168.1." + current_octet, 1884);
        scanner.on_stealthed = lan_on_stealthed;
        scanner.on_open_or_closed = lan_on_open_or_closed;
        scanner.run();
    }

    function lan_on_open_or_closed()
    {
        var res_div = document.getElementById("lan_results");
        res_div.innerHTML += "192.168.1." + current_octet + ": ";
        res_div.innerHTML += "Case 1 (" + this.total_time + " ms). <br />";

        current_octet += 1;

        if (stop || current_octet >= 255) {
            res_div.innerHTML += "Done. <br />";
            document.getElementById("lan_button").disabled = false;
            document.getElementById("lan_button_stop").disabled = true;
            return;
        }

        var scanner = new PortScanner("192.168.1." + current_octet, 1884);
        scanner.on_stealthed = lan_on_stealthed;
        scanner.on_open_or_closed = lan_on_open_or_closed;
        scanner.run();
    }

</script>



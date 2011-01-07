<?php

class DoorbotListener {

    function listen () {

        $socket = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
        socket_bind($socket, '0.0.0.0', 50000);

        while (true) {

            $buf = $from = $port = '';
            if (socket_recvfrom($socket, $buf, 1024, 0, $from, $port)) {

                list($event, $serial, $name) = explode("\n", $buf);

                if ($event == 'RFID' && $name) {
                    $this->doorOpened($serial, $name);

                } elseif ($event == 'RFID' && !$name) {
                    $this->unknownCard($serial);

                } elseif ($event == 'BELL') {
                    $this->doorbell();
                }
            }
        }
    }

    function doorOpened ($serial, $name) {}
    function unknownCard ($serial) {}
    function doorbell () {}
    function startup () {}

}

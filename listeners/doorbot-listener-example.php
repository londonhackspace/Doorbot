<?php

    require_once('DoorbotListener.class.php');

    class ExampleListener extends DoorbotListener {

        function doorOpened ($serial, $name) {
            print "The door was opened\n";
        }

        function unknownCard ($serial) {
            print "An unknown card was used on the door\n";
        }

        function doorbell () {
            print "The doorbell was pressed\n";
        }

        function startup () {
            print "Doorbot just started up\n";
        }

    }

    $listener = new ExampleListener();
    $listener->listen();

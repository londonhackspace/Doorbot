<?php

    require_once('../DoorbotListener.class.php');

    class ExampleListener extends DoorbotListener {

        function doorOpened ($serial, $name) {
            print "The door was opened by {$name}, card serial {$serial}.\n";
        }

        function unknownCard ($serial) {
            print "Unknown card {$serial} presented at the door.\n";
        }

        function doorbell () {
            print "Doorbell pressed.\n";
        }

        function startup () {
            print "Doorbot started.\n";
        }

    }

    $listener = new ExampleListener();
    $listener->listen();

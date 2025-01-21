This hand was designed, manufactured and assembled in under 15 hours, so there are quite a few issues/things to know listed below. If you want to build the hand without modifying the CAD files, follow the suggestions below. Instructions below include some basic assembly, modifications and recommendations.

M2 screws are used at all of the finger joints and used to fix the fishing line at the tips of the fingers. Holes are sized for M2 tap and can be self threaded by screwing a fastener into the plastic.

The index finger servo (closest to wrist connector), middle finger servo (next to index servo) and thumb grasp servo all need one mounting tab to be cut off from the side where the wires come out.

The 20T servo pulley has really small features (0.5mm holes, tiny splines). The printer used did not provide enough resolution so the internal splines were drilled out and pressed onto the servo shafts and the 0.5mm holes to mount the fishing line to the pulley was drilled out.

The thumb grasp servo is just in the wrong place and hits everything. It needs to rotate 90 degrees as seen in "Thumb Servo Modifications.PNG", and then you need to super glue ~2mm of material between the thumb rotate piece and the servo to give it enough clearance (the thumb grasp actuator is not completely necessary, all of our VR demos do not use it).

The palm needs a lot more clearance for the thumb rotation to work properly. See "Palm Modifications.PNG", Red indicates area to remove material, green represents areas to add material and yellow are areas you might need to file down for clearance. The green additions to the palm provide cable routing for the index finger fishing line so it clears the thumb rotation subassembly. The index finger 2mm hole might need to be drilled out a bit.

Add support blockers on all of the 2 mm holes in the fingers/palm where fishing line will go through, it will be difficult to clear supports and most printers should be fine printing without.

The index and middle finger servos are pressed into the palm, if they are loose use some super glue at the top to secure them.

To assemble, assemble each finger individually with fasteners and route fishing line through the finger. Mount the middle and ring fingers first, you will have to use pliers to start the thread because there isn't clearance for a screwdriver (unless you have a flexible extension i.e. in the ifixit kit). Then mount the pinky and index fingers. Attach the thumb to the thumb rotation piece and route fishing line through.

Set each servo to 180 degrees (or zero depending on direction, just make sure it can spin 180 degrees and it pulls the fishing line in tension) then press on the pulleys and make sure a line between the fishing line hole and the center of the pulley will be perpendicular to the fishing line. This ensures that as the servo rotates, the fishing line stays within the groove.

Start with the pinky servo, tie on the fishing line and knot it (dab super glue if you don't trust your knots), then mount the servo to the palm, then pull the fishing line coming out of the end of the finger to tension. Do the same for the ring finger.

Index and middle finger servos should be pressed/pushed into casing at back of palm. Route fishing to pulleys, then superglue cable routers to ensure fishing line avoids hitting anything (thumb parts). Route the index finger fishing line straight to the servo but loop over the added green material so that the fishing line runs parallel to the long side of the servo (this avoids the index finger from being actuated when the thumb rotation is used).

Zero the thumb rotation servo so that 180 degrees rotates the thumb parallel to the index finger. Mount the thumb subassembly to the thumb rotation servo (press fit, glue if necessary). Press the thumb pin into the bottom of the thumb rotation piece and through the hole in the palm (may have to drill out).

Super glue rubber bands as return springs to the tips of the fingers and to the base of the fingers. Be careful not to let super glue get into the cracks. Sprinkle baking soda on the joints to instant cure the superglue if it takes too long to dry. Rubber band tension should be enough to return fingers to open position, but not too much that the fishing line mechanism is overly stressed. Glue cable routers to ensure rubber bands stay inline on the fingers if necessary.

The middle finger has too much range of motion at the 2nd joint which ends up creating a bistable mechanism with the rubber band. Super glue some plastic in the joint to slightly limit the range of motion.

If any fingers have too much friction, loosen the joint screws, sand stuff down or use some lubricant.

The U-bracket at the bottom of the hand connects to the Zeroth Bot elbow joint. If you look at the hand palm down, the right side is super strong and the left side is really weak. Nothing has broken yet but material should be added to connect from the left side of the U-bracket to just above/to the left of the thumb servo.

Add some grippy material to the hand. I used double sided foam tape with rubber bands on top. Rubber bands fell off so I'd recommend just super gluing rubber bands to the hand.

Once assembled, use the default servo knob script in the Arduino IDE to find the actual min/max range of each servo.

You can hook everything up with VR or I attached a script the runs on an ESP32-C3 (use esp32_bluepad32 boards) and connects to an xbox one remote to control the hand. Works decently enough to do some simple demos.

import scala.collection.mutable.ListBuffer

object Main extends App {
  //whether to continue to run the background process
  var process = true

  //name of codes information file
  val codesFile = "codes.txt"

  //spool up
  Codes.init()
  PacketReceiver.start()

  var c = Codes.map.getOrElse("0x000", new Code(null, new ListBuffer[Field]))
  System.out.println(c.name)

  while(true) {
    Thread.sleep(50)
    while (PacketReceiver.packetBuffer.nonEmpty) {
      val k = PacketReceiver.packetBuffer.remove(0)
      for (by <- k) {
        print(by + " ")
      }
      println()
    }
  }
}

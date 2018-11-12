import java.net.{DatagramPacket, InetAddress, MulticastSocket}

import scala.collection.mutable.ListBuffer

object PacketReceiver extends Thread {
  val packetBuffer: ListBuffer[Array[Byte]] = new ListBuffer[Array[Byte]]

  private val mcastPort: Integer = 4876
  private val mcastAddr: InetAddress = InetAddress.getByName("239.255.60.60")
  private val mcastSocket: MulticastSocket = new MulticastSocket(mcastPort)
  try {
    mcastSocket.joinGroup(mcastAddr)
  } catch {
    case e: Exception =>
      println("Error opening socket. Is everything on/connected?")
      System.exit(1)
  }

  /**
    * Begins dumping packet data to public member packetBuffer
    */
  override def run(): Unit = {
    while (Main.process) {
      var localBuffer: Array[Byte] = new Array[Byte](80)
      val packet: DatagramPacket = new DatagramPacket(localBuffer, localBuffer.length)
      mcastSocket.receive(packet) //dump packet data into localBuffer
      packetBuffer += localBuffer
    }
  }
}

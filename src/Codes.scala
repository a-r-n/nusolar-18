import java.io.File
import java.util.Scanner

import scala.collection.mutable
import scala.collection.mutable.ListBuffer

object Codes {
  val map = new mutable.HashMap[String, Code]
  def init(): Unit = {
    val file = new File(Main.codesFile)
    val in = new Scanner(file)
    try {
      while (in.hasNext()) {
        val code = in.nextLine()
        val name = in.nextLine()

        val fields = new ListBuffer[Field]

        var line: String = in.nextLine()
        while (!line.equals("X")) {
          val f_name = line
          val f_size = Integer.parseInt(in.nextLine())
          fields += new Field(f_name, f_size)
          line = in.nextLine()
        }
        map += (code -> new Code(name, fields))
      }
    } catch {
      case e: Exception => System.out.println("Error reading codes file: " + e)
    }
  }
}

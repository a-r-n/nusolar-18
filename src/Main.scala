import scala.collection.mutable.ListBuffer

object Main extends App {
  val codesFile = "codes.txt"

  Codes.init()
  var c = Codes.map.getOrElse("0x000", new Code(null, new ListBuffer[Field]))
  System.out.println(c.name)
}

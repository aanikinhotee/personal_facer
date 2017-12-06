<?php


$fp = fopen('/dev/ttyACM0', 'rw');
fwrite($fp, "HA=60;\r\n");
$contents = '';
while (!feof($fp)) {
  $contents .= fread($fp, 8192);
}
echo $contents;
echo stream_get_contents($fp);
fwrite($fp, "VA=90;\r\n");
echo "VA";
echo stream_get_contents($fp);

fclose($fp);



?>

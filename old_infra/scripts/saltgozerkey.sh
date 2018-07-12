for i in {1..58}; do

salt node$i.pnap.ny.boinc cmd.run "echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDILlvk8UpAizSR2gC2QpCZIZv2DFuURaCBEHzmfcgP4RXTq9gPG3EqRALAAds+MjtbkQhNgvbMwD0lF6XrurVwyQ0mSQgzl0YqYqcPaVxTKO2hGlxpGqT3gQlVWscFDdzWhJH52OZ9PzxR7XwaAqzlGDv0sAYgmzBG4BMLg1LSQ0XDHEoBO/2WMcqsIjpSbqunrHeBzmCTh1u6EcDXW88qN7T/NiSis9qjnD/rw8mXuZ8AQ7bZk9gNr56ZAGCvVv+Tb9aNG7GBDbclRyBp5p57MdhemnZPEGTFJj5jPSECE4bsN5I61dUjSyW/9Ja/whA55c845iszfyLVtfSfTizd tech@boinc.com
' >> /home/jenkins/.ssh/authorized_keys"
#salt node$i.pnap.ny.boinc cmd.run "cp -f /srv/vm/gozerkey /home/gozer/.ssh/authorized_keys;chmod 644 /home/gozer/.ssh/authorized_keys;chown gozer:gozer /home/gozer/.ssh/authorized_keys;"
done


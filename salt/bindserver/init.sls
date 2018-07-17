#apt-get install -y bind9:
#  cmd.run
bind9:
  pkg.installed:
   - skip_verify: True

bindconfig:
  file.managed:
    - source: salt://bindserver/named.conf
    - name: /etc/bind/named.conf
    - user: root
    - group: bind
    - mode: 644
    - require:
      - pkg: bind9

/etc/bind/named.conf.openknetworks-zones:
  file.managed:
    - source: salt://bindserver/named.conf.openknetworks-zones
    - user: root
    - group: bind
    - mode: 644

/etc/bind/db.openknetworks.com:
  file.managed:
    - source: salt://bindserver/db.openknetworks.com
    - user: root
    - group: bind
    - mode: 644

/etc/bind/named.conf.options:
  file.managed:
    - source: salt://bindserver/named.conf.options
    - user: root
    - group: bind

service bind9 restart:
  cmd.run

tcpproxy_config_dir:
    file.directory:
        - name: /etc/nginx/stream.d
        - user: root
        - group: root
        - mode: 755
        - makedirs: True

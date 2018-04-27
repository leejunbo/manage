def add_host_file(args1, args2):
    f = open("F:/software/python/win/nginx-1.12.2/conf/conf.d/" + args1 + ".conf", "w", encoding='utf8')
    f.write(
        "\tserver{ \n"
        "\t\tlisten    80;\n"
        "\t\tserver_name  " + args1 + ";\n"
        "\t\tlocation / {\n"
        "\t\t\tproxy_pass http://" + args2 + ":8000;\n"
        "\t\t\tproxy_redirect off;\n"
        "\t\t\tproxy_set_header Host $host:80;\n"
        "\t\t\tproxy_set_header X-Real-IP $remote_addr;\n"
        "\t\t\tproxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
        "\t\t\tproxy_connect_timeout 600;\n"
        "\t\t\tproxy_read_timeout 600;\n"
        "\t\t}\n"
        "\t}\n")
    f.close()
    h = open("C:/Windows/System32/drivers/etc/hosts", "a+", encoding='utf8')
    h.write(args2 + "   " + args1 + "\n")
    h.close()

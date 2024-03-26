cat <<EOF
server:
  port: 8082
  log_level: "INFO"
  allowed_origins: ["*"]
apisix:
  key_path: $secret://vault/dev/
  instances:
    - name : "EWC"
      admin_url: http://127.0.0.1:9180
      gateway_url: http://127.0.0.1:9080
      admin_api_key: edd1c9f034335f136f87ad84b625c8f1
vault:
  url: http://127.0.0.1:8200
  base_path: apisix-dev/consumers/ewc
  token: 00000000-0000-0000-0000-000000000000
  secret_phase: geeks
keycloak:
  url: http://127.0.0.1:8080
  realm: test
EOF
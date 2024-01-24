package com.apiportal.backend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.vault.authentication.TokenAuthentication;
import org.springframework.vault.client.VaultEndpoint;
import org.springframework.vault.core.VaultTemplate;

@Configuration
public class VaultConfig {
    @Value("${vault.endpoint}")
    private String endpoint;

    @Value("${vault.scheme}")
    private String scheme;

    @Value("${vault.port}")
    private int port;

    @Value("${vault.token}")
    private String token;

    @Bean
    VaultTemplate vaultTemplate() {
        VaultEndpoint vaultEndpoint = new VaultEndpoint();

        vaultEndpoint.setHost(endpoint);
        vaultEndpoint.setPort(port);
        vaultEndpoint.setScheme(scheme);

        VaultTemplate vaultTemplate = new VaultTemplate(
                vaultEndpoint,
                new TokenAuthentication(token));

        return vaultTemplate;
    }
}

package com.apiportal.backend.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.vault.core.VaultKeyValueOperations;
import org.springframework.vault.core.VaultKeyValueOperationsSupport;
import org.springframework.vault.core.VaultOperations;
import org.springframework.vault.core.VaultTemplate;
import org.springframework.vault.support.VaultResponse;
import org.springframework.web.client.HttpStatusCodeException;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

@Service
public class VaultService {
    @Autowired
    VaultTemplate vaultTemplate;

    @Autowired
    ApiKeyService apiKeyService;

    @Value("${apisix.keyName}")
    private String keyName;

    public String saveUserToVault(String userName) {
        String generatedApiKey = apiKeyService.generateMD5Hashvalue(userName);
        VaultOperations operations = vaultTemplate;
        VaultKeyValueOperations keyValueOperations = operations.opsForKeyValue("apisix",
                VaultKeyValueOperationsSupport.KeyValueBackend.unversioned());

        Map vaultValues = new HashMap<>();
        vaultValues.put(keyName,generatedApiKey);
        vaultValues.put("date",getDate());

        try {
            keyValueOperations.put(userName, vaultValues);
        } catch (Exception e) {
            throw e;
        }
        return generatedApiKey;
    }

    public VaultResponse getUserinfoFromVault(String username) {
        VaultOperations operations = vaultTemplate;

        VaultResponse read = null;
        try {
            read = operations.read("apisix/" +username);
        } catch (HttpStatusCodeException e) {
            throw e;
        } catch (NoSuchMethodError e) {
            return null;
        }
        return read;
    }

    private String getDate() {
        DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm:ss");
        LocalDateTime now = LocalDateTime.now();
        String dateString = dtf.format(now);
        return dateString;
    }

}

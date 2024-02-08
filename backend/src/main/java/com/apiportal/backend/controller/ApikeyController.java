package com.apiportal.backend.controller;

import com.apiportal.backend.models.MessageObject;
import com.apiportal.backend.models.ServerStatus;
import com.apiportal.backend.models.VaultApiInfo;
import com.apiportal.backend.service.VaultService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.apiportal.backend.apisix.ApisixRestClient;
import com.apiportal.backend.infra.security.annotation.AllowedRoles;
import com.apiportal.backend.models.User;
import lombok.extern.slf4j.Slf4j;
import org.json.JSONException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClientException;

import java.util.List;


@RestController
@Slf4j
public class ApikeyController {

    @Autowired
    VaultService vaultService;
    @Autowired
    ApisixRestClient apisixRestClient;

    public ApikeyController() {

    }

    @GetMapping("/getapikey")
    @AllowedRoles("ADMIN")
    public ResponseEntity getApikey(){
        SecurityContext sc = SecurityContextHolder.getContext();
        sc.getAuthentication().getAuthorities().forEach(b -> log.info(b.toString()));

        //get user name we use this as id to save to vault and apisix
        String userName = sc.getAuthentication().getName();

        //check if servers are online and if user exists
        ServerStatus serverStatus = checkVaultAndApisix(userName);

        //if vault or apisix is offline we should not save any new user information
        if (!serverStatus.isApisixOnline() || !serverStatus.isVaultOnline()) {
            if (!serverStatus.isApisixOnline()) {
                return ResponseEntity
                        .status(HttpStatus.SERVICE_UNAVAILABLE)
                        .body(new MessageObject("Apisix server error"));
            }
            else if (!serverStatus.isVaultOnline()) {
                return ResponseEntity
                        .status(HttpStatus.SERVICE_UNAVAILABLE)
                        .body(new MessageObject("Vault server error"));
            }

        }

        //both servers seem to be online lets return key if user is allready saved
        String savedApikey = null;
        User createdUser = new User();
        createdUser.setUserName(userName);

        if (!serverStatus.isApisixUserFound()) {
            //save user to apisix
            createApisixUser(userName);
        }

        if (!serverStatus.isVaultUserFound()) {
            savedApikey = vaultService.saveUserToVault(userName);
            createdUser.setApiKey(savedApikey);
        }
        else {
            createdUser.setApiKey(serverStatus.getVaultApiInfo().getApiKey());
        }

        //get routes
        createdUser.setRoutes(getRoutes());

        return  ResponseEntity.status(HttpStatus.OK).body(createdUser);
    }



    private List<String> getRoutes() {
        try {
            List<String> routes = apisixRestClient.getRoutes();
            return routes;
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }
    }
    private void createApisixUser(String userName) {
        try {
            apisixRestClient.createConsumer(userName);
        } catch (JSONException e) {
            throw new RuntimeException(e);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    private ServerStatus checkVaultAndApisix(String userName) {
        ServerStatus serverStatus = new ServerStatus();
        try {
            boolean found = apisixRestClient.checkIfUserExists(userName);
            serverStatus.setApisixUserFound(found);
            serverStatus.setApisixOnline(true);
        } catch (RestClientException e) {
            serverStatus.setApisixOnline(false);
        }
        try {
            VaultApiInfo vaultApiInfo = vaultService.checkIfUserExists(userName);
            if (vaultApiInfo != null) {
                serverStatus.setVaultUserFound(true);
                serverStatus.setVaultApiInfo(vaultApiInfo);
            }
            serverStatus.setVaultOnline(true);
        } catch (RestClientException e) {
            serverStatus.setVaultOnline(false);
        }
        return serverStatus;
    }
}

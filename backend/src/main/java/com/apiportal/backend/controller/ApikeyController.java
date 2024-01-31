package com.apiportal.backend.controller;

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
import org.springframework.vault.support.VaultResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;


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

        //check if user is allready in vault
        VaultResponse vaultResponse = vaultService.getUserinfoFromVault(userName);

        String savedApikey = null;
        User createdUser = new User();
        createdUser.setUserName(userName);

        //if vault response is null it means user is not saved in there
        if (vaultResponse == null) {
//            return ResponseEntity
//                    .status(HttpStatus.FORBIDDEN)
//                    .body("Error Message");
            //save user to vault and return generated api key
            savedApikey = vaultService.saveUserToVault(userName);
            createdUser.setApiKey(savedApikey);

            //save user to apisix
            createApisixUser(userName);
        }
        else {
            createdUser.setApiKey(vaultResponse.getData().get("api-key").toString());
        }





        return  ResponseEntity.status(HttpStatus.OK).body(createdUser);
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
}

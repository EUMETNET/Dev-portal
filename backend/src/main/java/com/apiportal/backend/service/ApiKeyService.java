package com.apiportal.backend.service;

import org.springframework.stereotype.Service;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

import static java.nio.charset.StandardCharsets.UTF_8;

@Service
public class ApiKeyService {
    public String generateMD5Hashvalue(String userName)
    {
        LocalDate dateObj = LocalDate.now();
        DateTimeFormatter formatter
                = DateTimeFormatter.ofPattern("yyyyMMdd");
        String date = dateObj.format(formatter);

        MessageDigest md;
        try {
            md = MessageDigest.getInstance("MD5");
        }
        catch (NoSuchAlgorithmException e) {
            throw new IllegalArgumentException(e);
        }
        String secretPhase
                = "geeks"; // exclusively to set for geeks
        System.out.println("Current Date : " + date);
        System.out.println("Login Id : " + userName);
        System.out.println("Secret Phase : " + secretPhase);

        // By using the current date, userName(emailId) and
        // the secretPhase , it is generated
        byte[] hashResult
                = md.digest((date + userName + secretPhase)
                .getBytes(UTF_8));
        // convert the value to hex
        String password = bytesToHex(hashResult);
        System.out.println("Generated password.."
                + password);

        return password;
    }

    private String bytesToHex(byte[] bytes)
    {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}

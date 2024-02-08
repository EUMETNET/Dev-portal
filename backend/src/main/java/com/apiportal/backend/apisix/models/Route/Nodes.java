
package com.apiportal.backend.apisix;

import java.util.LinkedHashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "httpbin.org:80"
})
@Generated("jsonschema2pojo")
public class Nodes {

    @JsonProperty("httpbin.org:80")
    private Integer httpbinOrg80;
    @JsonIgnore
    private Map<String, Object> additionalProperties = new LinkedHashMap<String, Object>();

    @JsonProperty("httpbin.org:80")
    public Integer getHttpbinOrg80() {
        return httpbinOrg80;
    }

    @JsonProperty("httpbin.org:80")
    public void setHttpbinOrg80(Integer httpbinOrg80) {
        this.httpbinOrg80 = httpbinOrg80;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperty(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

}

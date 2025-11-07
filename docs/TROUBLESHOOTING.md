## Troubleshooting

### Connection Errors

#### ❌ "Cannot connect to server"

**Possible Causes:**
- Server is not running
- Incorrect URL format
- Firewall blocking connection
- Wrong port number

**Solutions:**
```bash
# 1. Verify server is running
# 2. Check URL format: opc.tcp://hostname:port
# 3. Test network connectivity
ping hostname

# 4. Check firewall rules (common OPC UA ports: 4840, 4840)
# 5. Try basic connection without security
python -m opc_browser.cli browse -s opc.tcp://localhost:4840
```

---

#### ❌ "Authentication failed"

**Error Hints:**
- `BadIdentityTokenRejected`: Wrong username/password or user doesn't exist
- `BadUserAccessDenied`: User exists but lacks permissions

**Solutions:**
```bash
# 1. Verify credentials
# 2. Check user exists on server
# 3. Confirm user has required permissions
# 4. Try without username/password if server allows anonymous
python -m opc_browser.cli browse -s opc.tcp://server:4840
```

---

#### ❌ "BadSecurityChecksFailed"

**Meaning:** Server rejected the client certificate

**Solutions:**
1. **Generate compatible certificate:**
   ```bash
   python -m opc_browser.cli generate-cert --uri "urn:matching:server:uri"
   ```

2. **Add certificate to server trust list** (server-specific process)

3. **Verify Application URI matches:**
   ```bash
   # Check server requirements for Application URI
   # Generate certificate with matching URI
   python -m opc_browser.cli generate-cert --uri "urn:server:required:uri"
   ```

4. **Check certificate validity:**
   - Not expired
   - Proper format (PEM vs DER)
   - Correct file permissions

---

### Node ID Errors

#### ❌ "BadNodeIdUnknown"

**Meaning:** Specified node doesn't exist in server's address space

**Solutions:**
```bash
# 1. Browse from root to find valid nodes
python -m opc_browser.cli browse -s opc.tcp://server:4840 -d 2

# 2. Look for NodeId hints in output:
#    💡 NodeId: ns=2;i=1000

# 3. Use discovered NodeId
python -m opc_browser.cli browse -s opc.tcp://server:4840 -n "ns=2;i=1000"
```

---

#### ❌ "Invalid Node ID format"

**Valid Formats:**
- `i=84` - Numeric in namespace 0
- `ns=2;i=1000` - Numeric with namespace
- `ns=2;s=MyNode` - String identifier
- `ns=2;g=uuid` - GUID identifier
- `ns=2;b=base64` - Opaque identifier

**Common Mistakes:**
```bash
# ❌ Wrong: Missing identifier after ns=
-n "ns=2"

# ✅ Correct: Complete node ID
-n "ns=2;i=1000"

# ❌ Wrong: Missing ns= prefix for string IDs
-n "s=MyNode"

# ✅ Correct: String ID with namespace
-n "ns=2;s=MyNode"
```

---

### Security Errors

#### ❌ "Certificate and private key are required"

**Meaning:** Security policy requires certificates but none provided

**Solution:**
```bash
# Generate certificates first
python -m opc_browser.cli generate-cert

# Then use in command
python -m opc_browser.cli browse -s opc.tcp://server:4840 --security Basic256Sha256 --mode SignAndEncrypt --cert certificates/client_cert.pem --key certificates/client_key.pem
```

---


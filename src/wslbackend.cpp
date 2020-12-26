/***************************************

    wslwinreg helper function

    Copyright (c) 2020 by Rebecca Ann Heineman <becky@burgerbecky.com>

    It is released under an MIT Open Source license. Please see LICENSE for
    license details. Yes, you can use it in a commercial title without paying
    anything, just give me a credit.

    Please? It's not like I'm asking you for money!

***************************************/

#include <windows.h>
#include <winsock2.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef ARRAYSIZE
#define ARRAYSIZE(a) (sizeof(a) / sizeof((a)[0]))
#endif

// Get rid if annoying visual studio warnings

// No pointer arithmetic
// https://docs.microsoft.com/en-us/cpp/code-quality/c26481
#pragma warning(disable : 26481)

// Use Notnull https://docs.microsoft.com/en-us/cpp/code-quality/c26429
#pragma warning(disable : 26429)

// No casts for Arithmetic conversion
// https://docs.microsoft.com/en-us/cpp/code-quality/c26472
#pragma warning(disable : 26472)

// No reinterpret cast, sorry, I like reinterpret_cast<>
// https://docs.microsoft.com/en-us/cpp/code-quality/c26490
#pragma warning(disable : 26490)

// No const cast, sorry, I like const_cast<>
// https://docs.microsoft.com/en-us/cpp/code-quality/c26492
#pragma warning(disable : 26492)

// Commands issued from the python script, must match
// class Commands(Enum) in wslapi.py

enum Commands : unsigned char {
    ABORT = 0,
    CONNECT = 1,
    CLOSE_KEY = 2,
    CONNECT_REGISTRY = 3,
    CREATE_KEY = 4,
    CREATE_KEY_EX = 5,
    DELETE_KEY = 6,
    DELETE_KEY_EX = 7,
    DELETE_VALUE = 8,
    ENUM_KEY = 9,
    ENUM_VALUE = 10,
    EXPAND_ENVIRONMENTSTRINGS = 11,
    FLUSH_KEY = 12,
    LOAD_KEY = 13,
    OPEN_KEY = 14,
    OPEN_KEY_EX = 15,
    QUERY_INFO_KEY = 16,
    QUERY_VALUE = 17,
    QUERY_VALUE_EX = 18,
    SAVE_KEY = 19,
    SET_VALUE = 20,
    SET_VALUE_EX = 21,
    DISABLE_REFLECTION_KEY = 22,
    ENABLE_REFLECTION_KEY = 23,
    QUERY_REFLECTION_KEY = 24
};

/***************************************

    Initialize WinSock 2.2

***************************************/

static int StartWinSock(void)
{
    WSADATA wsadata;
    return WSAStartup(MAKEWORD(2, 2), &wsadata);
}

/***************************************

    Shutdown WinSock 2.2

***************************************/

static void StopWinSock(void)
{
    WSACleanup();
}

/***************************************

    Create a local INET socket to listen for messages from
    Linux.

***************************************/

#if 0
static int ListenLocalSocket(int port, SOCKET* pOutSocket)
{
    // Assume failure
    *pOutSocket = INVALID_SOCKET;

    // Create the socket
    SOCKET sock = WSASocketW(
        AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, WSA_FLAG_OVERLAPPED);
    int iResult;
    if (sock == INVALID_SOCKET) {
        iResult = WSAGetLastError();
    } else {
        // Set the optional flags
        const char flag = true;
        iResult =
            setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
        if (!iResult) {

            // Set the port and address (LOOPBACK)
            sockaddr_in addr = {};
            addr.sin_family = AF_INET;
            addr.sin_port = htons(static_cast<short>(port));
            addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
            iResult =
                bind(sock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
            if (iResult) {
                iResult = WSAGetLastError();
            } else {
                // Start listening
                iResult = listen(sock, 1);
            }
        }

        // If no error, return the socket
        if (!iResult) {
            *pOutSocket = sock;
        } else {
            // Clean up
            closesocket(sock);
        }
    }
    return iResult;
}
#endif

/***************************************

    Connect to a socket created by wslwinreg

***************************************/

static int ConnectLocalSocket(int iPort, SOCKET* pOutSocket)
{
    // Assume failure
    *pOutSocket = INVALID_SOCKET;

    // Create the socket
    SOCKET sock = WSASocketW(
        AF_INET, SOCK_STREAM, IPPROTO_TCP, nullptr, 0, WSA_FLAG_OVERLAPPED);

    int iResult;
    if (sock == INVALID_SOCKET) {
        iResult = WSAGetLastError();
    } else {
        // Set the optional flags
        const char bFlag = true;
        iResult =
            setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &bFlag, sizeof(bFlag));
        if (!iResult) {

            // Set the port and address (LOOPBACK)
            sockaddr_in addr;
            memset(&addr, 0, sizeof(addr));
            addr.sin_family = AF_INET;
            addr.sin_port = htons(static_cast<short>(iPort));
            addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
            iResult = WSAConnect(sock, reinterpret_cast<sockaddr*>(&addr),
                sizeof(addr), nullptr, nullptr, nullptr, nullptr);
            if (iResult) {
                iResult = WSAGetLastError();
            }
        }

        // If no error, return the socket
        if (!iResult) {
            *pOutSocket = sock;
        } else {
            // Clean up due to error
            closesocket(sock);
        }
    }
    return iResult;
}

/***************************************

    Convert UTF-16 to UTF-8 "C" string.

    iWideLength is in WCHARs, not bytes.
    Returns nullptr or a char * of the converted string, pOutputLength will
    get the output string length in bytes

***************************************/

static char* ConvertToUTF8(
    const WCHAR* pInput, int iWideLength, int* pOutputLength)
{
    // Assume return values of nothing
    pOutputLength[0] = 0;
    char* pOutput = nullptr;

    if (iWideLength) {

        // Get the length of the string
        const int iNewLength = WideCharToMultiByte(
            CP_UTF8, 0, pInput, iWideLength, nullptr, 0, nullptr, nullptr);
        if (iNewLength > 0) {

            // Create the buffer and do the translation
            pOutput = static_cast<char*>(malloc(iNewLength + 1));
            if (pOutput) {
                WideCharToMultiByte(CP_UTF8, 0, pInput, iWideLength, pOutput,
                    iNewLength, nullptr, nullptr);
                // Ensure it's a "C" string
                pOutput[iNewLength] = 0;
                pOutputLength[0] = iNewLength;
            }
        }
    }
    return pOutput;
}

/***************************************

    Convert UTF-8 to UTF-16

    Return a pointer to the wide string or nullptr. pOutputLength returns
    the length of the string in characters, not bytes.

***************************************/

static WCHAR* ConvertToUTF16(
    const char* pInput, int iLength, int* pOutputLength)
{
    WCHAR* pOutput = nullptr;
    pOutputLength[0] = 0;
    if (iLength) {
        // Get the length of the string
        const int iNewLength =
            MultiByteToWideChar(CP_UTF8, 0, pInput, iLength, nullptr, 0);
        if (iNewLength > 0) {

            // Create the buffer and do the translation
            pOutput = (LPWSTR)malloc((iNewLength + 1) * 2);
            if (pOutput) {
                MultiByteToWideChar(
                    CP_UTF8, 0, pInput, iLength, pOutput, iNewLength);
                pOutput[iNewLength] = 0;
                pOutputLength[0] = 0;
            }
        }
    }
    return pOutput;
}

/***************************************

    Convert the window message to UTF-8

***************************************/

static char* winerror_to_string(LRESULT iResult, int* pOutputLength)
{
    WCHAR* pResult = nullptr;
    char* pOutput = nullptr;
    DWORD len = FormatMessageW(FORMAT_MESSAGE_ALLOCATE_BUFFER |
            FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        // no message source
        nullptr, static_cast<DWORD>(iResult),
        // Default language
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPWSTR)&pResult, 0,
        nullptr);

    if (len == 0) {
        // Out of memory?
        char buffer[256];
        const int iLen = sprintf_s(buffer, sizeof(buffer), "Windows Error 0x%x",
                             static_cast<int>(iResult)) +
            1;
        pOutput = static_cast<char*>(malloc(iLen));
        if (pOutput) {
            strcpy_s(pOutput, iLen, buffer);
        }
        pOutput[iLen - 1] = 0;
        pOutputLength[0] = iLen - 1;

    } else {
        // Clean up the string as per Python 3.9
        while ((len > 0) &&
            (pResult[len - 1] <= L' ' || pResult[len - 1] == L'.')) {
            pResult[--len] = 0;
        }
        pOutput = ConvertToUTF8(pResult, len, pOutputLength);
    }
    if (pResult) {
        LocalFree(pResult);
    }
    return pOutput;
}

/***************************************

    Fetch an amount of data from the stream.

***************************************/

static LRESULT Fetch(SOCKET sendsocket, char* buffer, int iCount)
{
    // Standard sanity checks
    if (iCount < 0) {
        return ERROR_INVALID_PARAMETER;
    }

    // Is there any data remaining?
    while (iCount) {
        // Get data, blocking until all has arrived
        int iReceived = recv(sendsocket, buffer, iCount, 0);
        if (iReceived == SOCKET_ERROR) {
            return WSAGetLastError();
        }
        if (!iReceived) {
            return WSAENOTCONN;
        }
        // Accept the data that came in.
        iCount -= iReceived;
        buffer += iReceived;
    }

    return ERROR_SUCCESS;
}

/***************************************

    Send an amount of data to the stream.

***************************************/

static LRESULT Send(SOCKET sendsocket, const char* buffer, int iCount)
{
    // Standard sanity checks
    if (iCount < 0) {
        return ERROR_INVALID_PARAMETER;
    }

    // Is there any data remaining?
    while (iCount) {
        // Get data, blocking until all has arrived
        // Note: Ethernet MTU size is 1500 bytes, so limit
        // chunks to this maximum size.
        int iChunkSize = iCount < 1500 ? iCount : 1500;
        int iSent = send(sendsocket, buffer, iChunkSize, 0);
        if (iSent == SOCKET_ERROR) {
            return WSAGetLastError();
        }
        if (!iSent) {
            return WSAENOTCONN;
        }
        // Accept the data that came in.
        iCount -= iSent;
        buffer += iSent;
    }

    return ERROR_SUCCESS;
}
/***************************************

    Convert a UTF-16 string into a UTF-8 string
    and send the length followed by the string
    back to the python code.

***************************************/

static void SendUTF8String(
    SOCKET sendsocket, const WCHAR* pNewString, DWORD uNewSize)
{
    int iOutputLength = 0;
    char* pOutput = ConvertToUTF8(pNewString, uNewSize, &iOutputLength);

    // Prepare length for transmission
    DWORD uSendSize = static_cast<DWORD>(iOutputLength);

    // Transmit the string length
    Send(sendsocket, reinterpret_cast<char*>(&uSendSize), 4);
    if (uSendSize) {
        // Transmit the string
        Send(sendsocket, pOutput, uSendSize);
    }
    // Release the UTF-8 string
    if (pOutput) {
        free(pOutput);
    }
}

/***************************************

    Transmit LRESULT
    Output: DWORD Error + message if any

***************************************/

static void ReturnResult(SOCKET sendsocket, LRESULT iResult)
{
    // Store the error code as 4 bytes
    DWORD uDWORD = static_cast<DWORD>(iResult);
    Send(sendsocket, reinterpret_cast<char*>(&uDWORD), 4);

    // If there was an error, create the description string
    if (uDWORD) {
        int iOutputLength = 0;
        char* pFoo = winerror_to_string(iResult, &iOutputLength);
        uDWORD = static_cast<DWORD>(iOutputLength);
        Send(sendsocket, reinterpret_cast<char*>(&uDWORD), 4);
        if (uDWORD) {
            Send(sendsocket, pFoo, uDWORD);
        }
        if (pFoo) {
            free(pFoo);
        }
    }
}

/***************************************

    Fetch a UTF8 string and convert to UTF-16

***************************************/

static LRESULT FetchWideString(SOCKET sendsocket, WCHAR** ppWideString)
{
    ppWideString[0] = nullptr;
    DWORD uLength = 0;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&uLength), 4);
    if ((iResult == ERROR_SUCCESS) && uLength) {
        // Get the buffer
        char* pFoo = static_cast<char*>(malloc(uLength));
        if (!pFoo) {
            iResult = ERROR_OUTOFMEMORY;
        } else {
            // Read it in
            iResult = Fetch(sendsocket, pFoo, uLength);
            if (iResult == ERROR_SUCCESS) {
                // Convert to wide format for windows
                int iOutputLength = 0;
                ppWideString[0] = ConvertToUTF16(pFoo, uLength, &iOutputLength);
                if (!ppWideString[0]) {
                    iResult = ERROR_OUTOFMEMORY;
                }
            }
            free(pFoo);
        }
    }
    return iResult;
}

/***************************************

    Call RegCloseKey()
    Input: QWORD HKEY
    Output: DWORD Error + message if any

***************************************/

static void CloseKey(SOCKET sendsocket)
{
    __int64 buffer;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        // Got the HKEY
        HKEY hKey = reinterpret_cast<HKEY>(buffer);

        // Only execute if non-zero
        if (hKey) {
            // Issue the call
            iResult = RegCloseKey(hKey);
        }
    }
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegConnectRegistryW()
    Input: QWORD HKEY, DWORD string length, UTF-8 string
    Output: QWORD new key, DWORD Error + message if any

***************************************/

static void ConnectRegistry(SOCKET sendsocket)
{
    __int64 buffer; // Registry main key
    HKEY pResult = nullptr;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        WCHAR* pMachineName = nullptr;
        iResult = FetchWideString(sendsocket, &pMachineName);
        if (iResult == ERROR_SUCCESS) {
            // Issue the call
            iResult = RegConnectRegistryW(
                pMachineName, reinterpret_cast<HKEY>(buffer), &pResult);
            if (pMachineName) {
                free(pMachineName);
            }
            if (iResult) {
                pResult = nullptr;
            }
        }
    }
    // Transmit it back with or without the error message
    unsigned __int64 iNewKey = reinterpret_cast<unsigned __int64>(pResult);
    Send(sendsocket, reinterpret_cast<char*>(&iNewKey), 8);
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegCreateKeyW()
    Input: QWORD HKEY, DWORD string length, UTF-8 string
    Output: QWORD new key, DWORD Error + message if any

***************************************/

static void CreateKey(SOCKET sendsocket)
{
    __int64 buffer; // Registry main key
    HKEY pResult = nullptr;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        WCHAR* pSubKey = nullptr;
        iResult = FetchWideString(sendsocket, &pSubKey);
        if (iResult == ERROR_SUCCESS) {
            // Issue the call
            iResult = RegCreateKeyW(
                reinterpret_cast<HKEY>(buffer), pSubKey, &pResult);

            if (iResult) {
                pResult = nullptr;
            }
        }
        if (pSubKey) {
            free(pSubKey);
        }
    }
    // Transmit it back with or without the error message
    unsigned __int64 iNewKey = reinterpret_cast<unsigned __int64>(pResult);
    Send(sendsocket, reinterpret_cast<char*>(&iNewKey), 8);
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegCreateKeyExW()
    Input: QWORD HKEY, DWORD reserved, DWORD access, DWORD string length, UTF-8
        string
    Output: QWORD new key, DWORD Error + message if any

***************************************/

static void CreateKeyEx(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey;   // Registry main key
        DWORD m_Reserved; // Options
        DWORD m_Access;   // Requested access
    } buffer;
    HKEY pResult = nullptr;
    LRESULT iResult =
        Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8 + 4 + 4);
    if (iResult == ERROR_SUCCESS) {
        WCHAR* pSubKey = nullptr;
        iResult = FetchWideString(sendsocket, &pSubKey);
        if (iResult == ERROR_SUCCESS) {
            // Issue the call
            iResult = RegCreateKeyExW(reinterpret_cast<HKEY>(buffer.m_hKey),
                pSubKey, buffer.m_Reserved, nullptr, 0, buffer.m_Access,
                nullptr, &pResult, nullptr);
            if (pSubKey) {
                free(pSubKey);
            }
            if (iResult) {
                pResult = nullptr;
            }
        }
    }
    // Transmit it back with or without the error message
    unsigned __int64 iNewKey = reinterpret_cast<unsigned __int64>(pResult);
    Send(sendsocket, reinterpret_cast<char*>(&iNewKey), 8);
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegDeleteKeyW()
    Input: QWORD HKEY, DWORD string length, string
    Output: DWORD Error + message if any

***************************************/

static void DeleteKey(SOCKET sendsocket)
{
    __int64 buffer;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        WCHAR* pWString = nullptr;
        // Convert to UTF-16
        iResult = FetchWideString(sendsocket, &pWString);
        if (iResult == ERROR_SUCCESS) {
            // Issue the call
            HKEY hKey = reinterpret_cast<HKEY>(buffer);
            iResult = RegDeleteKeyW(hKey, pWString);
            if (pWString) {
                free(pWString);
            }
        }
    }
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegDeleteKeyExW()
    Input: QWORD HKEY, DWORD reserved, DWORD access, DWORD string length, UTF-8
        string
    Output: QWORD new key, DWORD Error + message if any

***************************************/

static void DeleteKeyEx(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey;   // Registry main key
        DWORD m_Reserved; // Options
        DWORD m_Access;   // Requested access
    } buffer;
    LRESULT iResult =
        Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8 + 4 + 4);
    if (iResult == ERROR_SUCCESS) {
        WCHAR* pSubKey = nullptr;
        iResult = FetchWideString(sendsocket, &pSubKey);
        if (iResult == ERROR_SUCCESS) {
            // Issue the call
            iResult = RegDeleteKeyExW(reinterpret_cast<HKEY>(buffer.m_hKey),
                pSubKey, buffer.m_Access, buffer.m_Reserved);
            if (pSubKey) {
                free(pSubKey);
            }
        }
    }
    // Transmit error message
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegDeleteValueW()
    Input: QWORD HKEY, DWORD string length, string
    Output: DWORD Error + message if any

***************************************/

static void DeleteValue(SOCKET sendsocket)
{
    __int64 buffer;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        WCHAR* pWString = nullptr;
        // Convert to UTF-16
        iResult = FetchWideString(sendsocket, &pWString);
        if (iResult == ERROR_SUCCESS) {
            // Issue the call
            HKEY hKey = reinterpret_cast<HKEY>(buffer);
            iResult = RegDeleteValueW(hKey, pWString);
            if (pWString) {
                free(pWString);
            }
        }
    }
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegEnumKeyExW()
    Input: QWORD HKEY, DWORD index
    Output: DWORD stringlength, name string, DWORD Error + message if any

***************************************/

static void EnumKey(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey; // Registry main key
        DWORD m_Index;  // Options
    } buffer;

    // Default return information
    WCHAR temp_buffer[256 + 1];
    DWORD uTempLength = 0;

    LRESULT iResult =
        Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8 + 4);

    if (iResult == ERROR_SUCCESS) {
        uTempLength = 256 + 1;
        iResult =
            RegEnumKeyExW(reinterpret_cast<HKEY>(buffer.m_hKey), buffer.m_Index,
                temp_buffer, &uTempLength, nullptr, nullptr, nullptr, nullptr);
        if (iResult != ERROR_SUCCESS) {
            uTempLength = 0;
        }
    }

    // Send the name
    SendUTF8String(sendsocket, temp_buffer, uTempLength);

    // Transmit error message
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegEnumValueW()
    Input: QWORD HKEY, DWORD index
    Output: DWORD stringlength, name string, DWORD data_length, data, DWORD
        utype, DWORD Error + message if any

***************************************/

static void EnumValue(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey; // Registry main key
        DWORD m_Index;  // Options
    } buffer;

    // Default return information
    DWORD uValueSize = 0;
    DWORD uDataSize = 0;
    WCHAR* pValueName = nullptr;
    BYTE* pDataValue = nullptr;
    DWORD uType = 0;

    LRESULT iResult =
        Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8 + 4);

    if (iResult == ERROR_SUCCESS) {
        iResult = RegQueryInfoKeyW(reinterpret_cast<HKEY>(buffer.m_hKey),
            nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
            &uValueSize, &uDataSize, nullptr, nullptr);
        if (iResult == ERROR_SUCCESS) {
            if (uDataSize < 256) {
                uDataSize = 256;
            }
            ++uValueSize;
            ++uDataSize;
            pValueName = static_cast<WCHAR*>(malloc(uValueSize * 2));
            pDataValue = static_cast<BYTE*>(malloc(uDataSize));
            if (!pValueName || !pDataValue) {
                iResult = ERROR_OUTOFMEMORY;
                uDataSize = 0;
                uValueSize = 0;
            } else {
                for (;;) {
                    DWORD uValueSize2 = uValueSize;
                    DWORD uDataSize2 = uDataSize;

                    iResult =
                        RegEnumValueW(reinterpret_cast<HKEY>(buffer.m_hKey),
                            buffer.m_Index, pValueName, &uValueSize, nullptr,
                            &uType, pDataValue, &uDataSize);
                    if (iResult != ERROR_MORE_DATA) {
                        // Get the true length of the name string
                        uValueSize = static_cast<DWORD>(wcslen(pValueName));
                        break;
                    }
                    uDataSize = uDataSize2 * 2;
                    uValueSize = uValueSize2;
                    free(pDataValue);
                    pDataValue = static_cast<BYTE*>(malloc(uDataSize));
                    if (!pDataValue) {
                        iResult = ERROR_OUTOFMEMORY;
                        uDataSize = 0;
                        uValueSize = 0;
                        break;
                    }
                }
            }
        }
    }

    // Send the name
    SendUTF8String(sendsocket, pValueName, uValueSize);
    // Send the data
    Send(sendsocket, reinterpret_cast<char*>(&uDataSize), 4);
    if (uDataSize) {
        Send(sendsocket, reinterpret_cast<char*>(pDataValue), uDataSize);
    }
    // Send the type
    Send(sendsocket, reinterpret_cast<char*>(&uType), 4);

    // Free the buffers
    if (pDataValue) {
        free(pDataValue);
    }
    if (pValueName) {
        free(pValueName);
    }
    // Transmit error message
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call ExpandEnvironmentStringsW()
    Input: DWORD string length, UTF-8 string
    Output: DWORD string length, string, DWORD Error + message if any

***************************************/

static void ExpandEnvironmentStringsBackEnd(SOCKET sendsocket)
{
    DWORD uNewSize = 0;
    WCHAR* pNewString = nullptr;

    WCHAR* pWString = nullptr;
    // Read in the string
    LRESULT iResult = FetchWideString(sendsocket, &pWString);
    if (iResult == ERROR_SUCCESS) {

        // Determine the length of the new string (With terminating zero)
        uNewSize = ExpandEnvironmentStringsW(pWString, nullptr, 0);
        if (uNewSize) {
            pNewString = static_cast<WCHAR*>(malloc(uNewSize * 2));
            if (pNewString) {
                // Perform the conversion
                ExpandEnvironmentStringsW(pWString, pNewString, uNewSize);
                --uNewSize;
                pNewString[uNewSize] = 0;
            } else {
                uNewSize = 0;
            }
        }
        if (pWString) {
            free(pWString);
        }
    }

    // Send the result string
    SendUTF8String(sendsocket, pNewString, uNewSize);
    if (pNewString) {
        free(pNewString);
    }

    // Send the error code
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegFlushKey()
    Input: QWORD HKEY
    Output: DWORD Error + message if any

***************************************/

static void FlushKey(SOCKET sendsocket)
{
    __int64 buffer;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        // Got the HKEY
        HKEY hKey = reinterpret_cast<HKEY>(buffer);

        // Issue the call
        iResult = RegFlushKey(hKey);
    }
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegLoadKeyW()
    Input: QWORD HKEY, DWORD string length, UTF-8 string,
        DWORD filename length, UTF-8 filename
    Output: DWORD Error + message if any

***************************************/

static void LoadKey(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey; // Registry main key
    } buffer;

    HKEY pResult = nullptr;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        WCHAR* pSubKey = nullptr;
        iResult = FetchWideString(sendsocket, &pSubKey);
        if (iResult == ERROR_SUCCESS) {
            WCHAR* pFileName = nullptr;
            iResult = FetchWideString(sendsocket, &pFileName);
            if (iResult == ERROR_SUCCESS) {
                // Issue the call
                iResult = RegLoadKeyW(
                    reinterpret_cast<HKEY>(buffer.m_hKey), pSubKey, pFileName);
            }
            if (pFileName) {
                free(pFileName);
            }
        }
        if (pSubKey) {
            free(pSubKey);
        }
    }
    // Transmit it back with or without the error message
    unsigned __int64 iNewKey = reinterpret_cast<unsigned __int64>(pResult);
    Send(sendsocket, reinterpret_cast<char*>(&iNewKey), 8);
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegOpenKeyExW()
    Input: QWORD HKEY, DWORD reserved, DWORD access, DWORD string length,
        UTF-8 string
    Output: QWORD new key, DWORD Error + message if any

***************************************/

static void OpenKey(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey;   // Registry main key
        DWORD m_Reserved; // Options
        DWORD m_Access;   // Requested access
    } buffer;

    HKEY pResult = nullptr;
    LRESULT iResult =
        Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8 + 4 + 4);
    if (iResult == ERROR_SUCCESS) {
        WCHAR* pSubKey = nullptr;
        iResult = FetchWideString(sendsocket, &pSubKey);
        if (iResult == ERROR_SUCCESS) {
            // Issue the call
            iResult = RegOpenKeyExW(reinterpret_cast<HKEY>(buffer.m_hKey),
                pSubKey, buffer.m_Reserved, buffer.m_Access, &pResult);
            if (pSubKey) {
                free(pSubKey);
            }
            if (iResult) {
                pResult = nullptr;
            }
        }
    }
    // Transmit it back with or without the error message
    unsigned __int64 iNewKey = reinterpret_cast<unsigned __int64>(pResult);
    Send(sendsocket, reinterpret_cast<char*>(&iNewKey), 8);
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegQueryInfoKeyW()
    Input: QWORD HKEY
    Output: DWORD Error + message if any

***************************************/

static void QueryInfoKey(SOCKET sendsocket)
{
    struct {
        DWORD uSubKeys;
        DWORD uValues;
        FILETIME sFileTime;
    } outputbuffer;

    outputbuffer.uSubKeys = 0;
    outputbuffer.uValues = 0;
    outputbuffer.sFileTime.dwHighDateTime = 0;
    outputbuffer.sFileTime.dwLowDateTime = 0;

    __int64 buffer;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        // Got the HKEY
        HKEY hKey = reinterpret_cast<HKEY>(buffer);
        // Issue the call
        iResult = RegQueryInfoKeyW(hKey, nullptr, nullptr, 0,
            &outputbuffer.uSubKeys, nullptr, nullptr, &outputbuffer.uValues,
            nullptr, nullptr, nullptr, &outputbuffer.sFileTime);
    }

    Send(sendsocket, reinterpret_cast<char*>(&outputbuffer), 4 + 4 + 8);
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegQueryValueW()
    Input: QWORD HKEY, string
    Output: DWORD stringlength, name string, DWORD Error + message if any

***************************************/

static void QueryValue(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey; // Registry main key
    } buffer;

    // Default return information
    LONG uDataSize = 0;
    WCHAR* pDataValue = nullptr;

    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);

    if (iResult == ERROR_SUCCESS) {
        WCHAR* pSubKey = nullptr;
        iResult = FetchWideString(sendsocket, &pSubKey);
        if (iResult == ERROR_SUCCESS) {
            if (!pSubKey) {
                // Wonderful, RegQueryValueW() reports invalid parameter
                // if this is nullptr, despite what the docs say
                pSubKey = static_cast<WCHAR*>(malloc(2));
                if (pSubKey) {
                    pSubKey[0] = 0;
                }
            }
            iResult = RegQueryValueW(reinterpret_cast<HKEY>(buffer.m_hKey),
                pSubKey, nullptr, &uDataSize);
            if (iResult == ERROR_MORE_DATA) {
                uDataSize = 256;
                iResult = ERROR_SUCCESS;
            }
            if (iResult == ERROR_SUCCESS) {
                pDataValue = static_cast<WCHAR*>(malloc(uDataSize));
                if (!pDataValue) {
                    iResult = ERROR_OUTOFMEMORY;
                    uDataSize = 0;
                } else {
                    for (;;) {
                        DWORD uDataSize2 = uDataSize;
                        iResult = RegQueryValueW(
                            reinterpret_cast<HKEY>(buffer.m_hKey), pSubKey,
                            pDataValue, &uDataSize);
                        if (iResult != ERROR_MORE_DATA) {
                            // Get the REAL length of the loaded string.
                            if (uDataSize >= 2) {
                                uDataSize = (uDataSize / 2) - 1;
                            }
                            break;
                        }
                        uDataSize = uDataSize2 * 2;
                        free(pDataValue);
                        pDataValue = static_cast<WCHAR*>(malloc(uDataSize));
                        if (!pDataValue) {
                            iResult = ERROR_OUTOFMEMORY;
                            uDataSize = 0;
                            break;
                        }
                    }
                }
            }
        }
        if (pSubKey) {
            free(pSubKey);
        }
    }

    // Send the data
    SendUTF8String(sendsocket, pDataValue, uDataSize);
    // Free the buffers
    if (pDataValue) {
        free(pDataValue);
    }
    // Send the result string
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegQueryValueExW()
    Input: QWORD HKEY, DWORD index
    Output: DWORD stringlength, name string, DWORD data_length, data, DWORD
        utype, DWORD Error + message if any

***************************************/

static void QueryValueEx(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey; // Registry main key
    } buffer;

    // Default return information
    DWORD uDataSize = 0;
    BYTE* pDataValue = nullptr;
    DWORD uType = 0;

    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);

    if (iResult == ERROR_SUCCESS) {
        WCHAR* pValueName = nullptr;
        iResult = FetchWideString(sendsocket, &pValueName);
        if (iResult == ERROR_SUCCESS) {
            if (!pValueName) {
                // Wonderful, RegQueryValueExW() reports invalid parameter
                // if this is nullptr, despite what the docs say
                pValueName = static_cast<WCHAR*>(malloc(2));
                if (pValueName) {
                    pValueName[0] = 0;
                }
            }
            iResult = RegQueryValueExW(reinterpret_cast<HKEY>(buffer.m_hKey),
                pValueName, nullptr, nullptr, nullptr, &uDataSize);
            if (iResult == ERROR_MORE_DATA) {
                uDataSize = 256;
                iResult = ERROR_SUCCESS;
            }
            if (iResult == ERROR_SUCCESS) {
                pDataValue = static_cast<BYTE*>(malloc(uDataSize));
                if (!pDataValue) {
                    iResult = ERROR_OUTOFMEMORY;
                    uDataSize = 0;
                } else {
                    for (;;) {
                        DWORD uDataSize2 = uDataSize;
                        iResult = RegQueryValueExW(
                            reinterpret_cast<HKEY>(buffer.m_hKey), pValueName,
                            nullptr, &uType, pDataValue, &uDataSize);
                        if (iResult != ERROR_MORE_DATA) {
                            break;
                        }
                        uDataSize = uDataSize2 * 2;
                        free(pDataValue);
                        pDataValue = static_cast<BYTE*>(malloc(uDataSize));
                        if (!pDataValue) {
                            iResult = ERROR_OUTOFMEMORY;
                            uDataSize = 0;
                            break;
                        }
                    }
                }
            }
        }
        if (pValueName) {
            free(pValueName);
        }
    }

    // Send the data
    Send(sendsocket, reinterpret_cast<char*>(&uDataSize), 4);
    if (uDataSize) {
        Send(sendsocket, reinterpret_cast<char*>(pDataValue), uDataSize);
    }
    // Send the type
    Send(sendsocket, reinterpret_cast<char*>(&uType), 4);

    // Free the buffers
    if (pDataValue) {
        free(pDataValue);
    }
    // Transmit error message
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegLoadKeyW()
    Input: QWORD HKEY, DWORD string length, UTF-8 string,
        DWORD filename length, UTF-8 filename
    Output: DWORD Error + message if any

***************************************/

static void SaveKey(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey; // Registry main key
    } buffer;

    HKEY pResult = nullptr;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        WCHAR* pFileName = nullptr;
        iResult = FetchWideString(sendsocket, &pFileName);
        if (iResult == ERROR_SUCCESS) {
            // Issue the call
            iResult = RegSaveKeyW(
                reinterpret_cast<HKEY>(buffer.m_hKey), pFileName, nullptr);
        }
        if (pFileName) {
            free(pFileName);
        }
    }

    // Transmit it back with or without the error message
    unsigned __int64 iNewKey = reinterpret_cast<unsigned __int64>(pResult);
    Send(sendsocket, reinterpret_cast<char*>(&iNewKey), 8);
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegSetValueW()
    Input: QWORD HKEY, DWORD sub_key name, value string
    Output: DWORD Error + message if any

***************************************/

static void SetValue(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey; // Registry main key
    } buffer;

    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);

    if (iResult == ERROR_SUCCESS) {
        WCHAR* pSubKeyName = nullptr;
        iResult = FetchWideString(sendsocket, &pSubKeyName);
        if (iResult == ERROR_SUCCESS) {
            WCHAR* pValue = nullptr;
            iResult = FetchWideString(sendsocket, &pValue);
            if (iResult == ERROR_SUCCESS) {
                DWORD uValueSize = 0;
                if (pValue) {
                    uValueSize = static_cast<DWORD>(wcslen(pValue));
                }
                iResult = RegSetValueW(reinterpret_cast<HKEY>(buffer.m_hKey),
                    pSubKeyName, REG_SZ, pValue, uValueSize);
                if (pValue) {
                    free(pValue);
                }
            }
            if (pSubKeyName) {
                free(pSubKeyName);
            }
        }
    }

    // Transmit error message
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegSetValueExW()
    Input: QWORD HKEY,DWORD reserved, DWORD type, DWORD value name, data
    Output: DWORD Error + message if any

***************************************/

static void SetValueEx(SOCKET sendsocket)
{
    struct {
        __int64 m_hKey; // Registry main key
        DWORD m_Type;   // Data type
    } buffer;

    LRESULT iResult =
        Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8 + 4);
    char* pData = nullptr;
    DWORD uLength = 0;

    if (iResult == ERROR_SUCCESS) {
        WCHAR* pValueName = nullptr;
        iResult = FetchWideString(sendsocket, &pValueName);
        if (iResult == ERROR_SUCCESS) {

            iResult = Fetch(sendsocket, reinterpret_cast<char*>(&uLength), 4);
            if ((iResult == ERROR_SUCCESS) && uLength) {
                // Get the buffer
                pData = static_cast<char*>(malloc(uLength));
                if (!pData) {
                    iResult = ERROR_OUTOFMEMORY;
                } else {
                    // Read it in
                    iResult = Fetch(sendsocket, pData, uLength);
                }
            }
            if (iResult == ERROR_SUCCESS) {
                iResult = RegSetValueExW(reinterpret_cast<HKEY>(buffer.m_hKey),
                    pValueName, 0, buffer.m_Type,
                    reinterpret_cast<BYTE*>(pData), uLength);
            }
            if (pData) {
                free(pData);
            }
            if (pValueName) {
                free(pValueName);
            }
        }
    }

    // Transmit error message
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegDisableReflectionKey()
    Input: QWORD HKEY
    Output: DWORD Error + message if any

***************************************/

static void DisableReflectionKey(SOCKET sendsocket)
{
    __int64 buffer;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        // Got the HKEY
        HKEY hKey = reinterpret_cast<HKEY>(buffer);

        // Issue the call
        iResult = RegDisableReflectionKey(hKey);
    }
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegEnableReflectionKey()
    Input: QWORD HKEY
    Output: DWORD Error + message if any

***************************************/

static void EnableReflectionKey(SOCKET sendsocket)
{
    __int64 buffer;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        // Got the HKEY
        HKEY hKey = reinterpret_cast<HKEY>(buffer);

        // Issue the call
        iResult = RegEnableReflectionKey(hKey);
    }
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Call RegQueryReflectionKey()
    Input: QWORD HKEY
    Output: BYTE result, DWORD Error + message if any

***************************************/

static void QueryReflectionKey(SOCKET sendsocket)
{
    __int64 buffer;
    BOOL bAnswer = FALSE;
    LRESULT iResult = Fetch(sendsocket, reinterpret_cast<char*>(&buffer), 8);
    if (iResult == ERROR_SUCCESS) {
        // Got the HKEY
        HKEY hKey = reinterpret_cast<HKEY>(buffer);

        // Issue the call
        iResult = RegQueryReflectionKey(hKey, &bAnswer);
        if (iResult != ERROR_SUCCESS) {
            bAnswer = FALSE;
        }
    }
    // Transmit it back with or without the error message
    char iNewKey = static_cast<char>(bAnswer);
    Send(sendsocket, &iNewKey, 1);
    ReturnResult(sendsocket, iResult);
}

/***************************************

    Process the socket information

***************************************/

static void ProcessCommands(SOCKET sendsocket)
{
    // Send the version number. Must match in wslapi.py
    Send(sendsocket, "Bridge started 1.0", 18);

    for (;;) {
        char buffer[32];
        // Wait for a command
        LRESULT iResult = Fetch(sendsocket, buffer, 1);
        if (iResult != ERROR_SUCCESS) {
            break;
        }
        // Process the command
        switch (buffer[0]) {
        case CLOSE_KEY:
            CloseKey(sendsocket);
            break;
        case CONNECT_REGISTRY:
            ConnectRegistry(sendsocket);
            break;
        case CREATE_KEY:
            CreateKey(sendsocket);
            break;
        case CREATE_KEY_EX:
            CreateKeyEx(sendsocket);
            break;
        case DELETE_KEY:
            DeleteKey(sendsocket);
            break;
        case DELETE_KEY_EX:
            DeleteKeyEx(sendsocket);
            break;
        case DELETE_VALUE:
            DeleteValue(sendsocket);
            break;
        case ENUM_KEY:
            EnumKey(sendsocket);
            break;
        case ENUM_VALUE:
            EnumValue(sendsocket);
            break;
        case EXPAND_ENVIRONMENTSTRINGS:
            ExpandEnvironmentStringsBackEnd(sendsocket);
            break;
        case FLUSH_KEY:
            FlushKey(sendsocket);
            break;
        case LOAD_KEY:
            LoadKey(sendsocket);
            break;
        case OPEN_KEY:
        case OPEN_KEY_EX:
            OpenKey(sendsocket);
            break;
        case QUERY_INFO_KEY:
            QueryInfoKey(sendsocket);
            break;
        case QUERY_VALUE:
            QueryValue(sendsocket);
            break;
        case QUERY_VALUE_EX:
            QueryValueEx(sendsocket);
            break;
        case SAVE_KEY:
            SaveKey(sendsocket);
            break;
        case SET_VALUE:
            SetValue(sendsocket);
            break;
        case SET_VALUE_EX:
            SetValueEx(sendsocket);
            break;
        case DISABLE_REFLECTION_KEY:
            DisableReflectionKey(sendsocket);
            break;
        case ENABLE_REFLECTION_KEY:
            EnableReflectionKey(sendsocket);
            break;
        case QUERY_REFLECTION_KEY:
            QueryReflectionKey(sendsocket);
            break;
        default:
            break;
        }
    }
}

/***************************************

    Main entry point.

    Command is -p 2056 with 2056 being the port to connect
    with from the python script wslwinreg.

***************************************/

int __cdecl main(int argc, char* argv[])
{
    // Default message in case the app was run by a user
    if (argc < 2) {
        fprintf(stderr, "%s is a helper application for wslwinreg.\n", argv[0]);
        return 1;
    }

    // Get the port to connect to by scanning for -p in the command list
    int iPort = 0;
    bool bPortFound = false;
    int i;
    for (i = 1; i < argc; ++i) {
        if (!_stricmp(argv[i], "-p")) {
            if ((i + 1) != argc) {
                iPort = atoi(argv[++i]);
                bPortFound = true;
                continue;
            }
        }
    }

    // Error?
    if (!bPortFound) {
        printf(
            "\nUsage: %s -p port\n"
            "\nbackend for wslwinreg\n"
            "This program should not be executed directly\n\n",
            argv[0]);
        return 1;
    }

    // Init WinSock
    int iResult = StartWinSock();
    if (iResult == ERROR_SUCCESS) {

        // Connect to the python script
        SOCKET sendsocket = INVALID_SOCKET;
        iResult = ConnectLocalSocket(iPort, &sendsocket);
        if (iResult == ERROR_SUCCESS) {
            ProcessCommands(sendsocket);
            closesocket(sendsocket);
        }
        StopWinSock();
    }
    return iResult;
}

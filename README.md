# vk_audio_downloader
little CLI app to download tracks from vk.

# Dependencies
```vk_api```   - 11.9.9<br>
```requests``` - 2.26.0<br>

# Overall
1. It's available on windows only.<br>
2. It has ability to download only tracks now.<br>


# How to use
1. set permission for foreign applications to get access to your account's music,<br>
Officially it is called access token for api.
After you will be able to use the application.

## Graphical mode
Now i added graphical mode. it's runned by default. You can find build of this application in build section.<br>
To run it within terminal - ```vk_audio_downloader.exe terminal```

## Command list
```scan``` - scan account's music to receive tracks in specified range. example : scan  10,100.<br>
After music is scanned to obtain name, artist and url, data is saved in local data base and then<br>
you can easily download it via ```find``` function.<br>

```size``` - get size of loaded data.<br>
```get``` - get list of tracks.<br>

```help``` - show this text.<br>
```clear``` - clear the terminal screen.<br>

```find``` - find substring in saved tracks/albums, also specify case sensitivity. example - find "wish yo" artist|track 0<br>
              where 0 means non case sensible.

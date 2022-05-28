## Copyright 2019-2022 Azariel Del Carmen (GanstaKingofSA). All rights reserved.

# gallery.rpy
# This file contains the code for the gallery menu that shows backgrounds and 
# sprites from your mod.
default enable_gallery = True

if enable_gallery:
    
    init python:
        galleryList = {} 
        current_img_name = None

        # This class declares the code to make a image for the gallery menu.
        # Syntax:
        #   image - This variable contains the path or image tag (sayori 1a) of the 
        #           image.
        #   small_size - This variable contain the path or image tag of a shorten version
        #                   of the image in the gallery.
        #   name - This variable contains the human-readable name of the image in the
        #           gallery.
        #   artist - This variable contains the human-readable author name of the image.
        #   sprite - This variable checks if the image declared is a character sprite.
        #   watermark - This variable checks if the exporter should export a watermarked image
        #               of the image shown in the gallery.
        #   unlocked - This variable checks if this image should be included in the gallery
        #               or until it is shown in-game.
        class GalleryImage:

            def __init__(self, image, small_size=None, name=None, artist=None, sprite=False, unlocked=True):
                global galleryList 

                # The image variable name in-game
                self.file = image

                # The human readable name of the image
                if name: self.name = name
                else: self.name = image

                # The human readable author of the image
                self.artist = artist

                # This condition sees if the image given is a sprite
                self.sprite = sprite

                self.unlocked_str = None

                # A condition to see if the image should be shown
                if unlocked is True: self.unlocked = True
                elif not unlocked: self.unlocked = renpy.seen_image(image)
                else: 
                    self.unlocked_str = unlocked
                    self.unlocked = eval(unlocked)

                if sprite:
                    self.image = Composite(
                        (config.screen_width, config.screen_height), (0, 0), 
                        "black", (0.2 * (config.screen_width / 1280.0), 0), 
                        Transform(image, zoom=0.75*0.95)
                    )

                    # A descaled version of the main image.
                    if small_size:
                        self.small_size = small_size 
                    else:               
                        self.small_size = Composite(
                            (234, 132), (0, 0), 
                            "black", (0.2, 0), 
                            Transform(image, zoom=0.137)
                        )
                else:
                    self.image = Transform(image, xysize=(config.screen_width, config.screen_height-40))

                    if small_size:
                        self.small_size = small_size 
                    else:     
                        self.small_size = Transform(image, xysize=(234, 132))

                galleryList[self.name] = self

            # This function exports the selected image to the players' computer.
            def export(self):
                if renpy.android:
                    try: os.mkdir(os.environ['ANDROID_PUBLIC'] + "/gallery")
                    except: pass
                else:
                    try: os.mkdir(config.basedir + "/gallery")
                    except: pass

                if self.sprite: renpy.show_screen("dialog", message="Sprites cannot be exported to the gallery folder. Please try another image.", ok_action=Hide("dialog"))
                else:
                    try: 
                        renpy.file(self.file)
                        export = self.file
                    except:
                        export = get_registered_image(self.file).filename
                        
                    if renpy.android:
                        with open(os.path.join(os.environ['ANDROID_PUBLIC'], "gallery", os.path.splitext(export)[0].split("/")[-1] + os.path.splitext(export)[-1]), "wb") as p:
                            p.write(renpy.file(export).read())
                    else:
                        with open(os.path.join(config.basedir, "gallery", os.path.splitext(export)[0].split("/")[-1] + os.path.splitext(export)[-1]).replace("\\", "/"), "wb") as p:
                            p.write(renpy.file(export).read())

                        renpy.show_screen("dialog", message='Exported "%s" to the gallery folder.' % self.name, ok_action=Hide("dialog"))

        class GalleryThread():
            def __init__(self):
                self.lock = threading.RLock()
                self.periodic_condition = threading.Condition()
                self.gallery_thread = threading.Thread(target=self.gallery_thread_main)
                self.gallery_thread.daemon = True
                self.gallery_thread.start()

            def gallery_thread_main(self):
                while True:
                    with self.periodic_condition:
                        self.periodic_condition.wait(1.0)

                    with self.lock:
                        for name, gl in galleryList.items():
                            if gl.unlocked_str is not None:
                                gl.unlocked = eval(gl.unlocked_str)

        gallery_image_thread = GalleryThread()

        # This function advances to the next/previous image in the gallery.
        def next_image(back=False):
            global current_img_name

            # Create a new list from the keys
            all_keys = list(galleryList.keys())

            # Get the current key as index
            current_index = all_keys.index(current_img_name)

            # Get the next key as index
            next_index = current_index - 1 if back else current_index + 1

            try: 
                all_keys[next_index]
                current_img_name = all_keys[next_index]
            except IndexError: current_img_name = all_keys[0]

        # For Ren'Py 6 compatibility. This function gets the image displayed in the
        # gallery from from 'renpy.display.image'.
        def get_registered_image(name): 

            if not isinstance(name, tuple):
                name = tuple(name.split())

            return imgcore.images.get(name)

        # This section declares the images to be shown in the gallery. See the
        # 'GalleryMenu' class syntax to declare a image to the gallery.
        residential = GalleryImage("bg residential_day")
        s1a = GalleryImage("sayori 1", sprite=True)
        m1a = GalleryImage("monika 1", name="Monika", artist="Satchely", sprite=True)

    ## Gallery Screen #############################################################
    ##
    ## This screen is used to make a gallery view of in-game art to the player in 
    ## the main menu.
    ##
    ## Syntax:
    ##   gl.image - This variable contains the path or image tag (sayori 1a) of the 
    ##              image.
    ##   gl.small_size - This variable contain the path or image tag of a shorten version
    ##                   of the image in the gallery.
    ##   gl.name - This variable contains the human-readable name of the image in the
    ##               gallery.
    ##   gl.sprite - This variable checks if the image declared is a character sprite.
    ##   gl.locked - This variable checks if this image should not be included in
    ##               the gallery until it is shown in-game.
    screen gallery():

        tag menu

        use game_menu(_("Gallery")):
            
            fixed:

                vpgrid:
                    id "gvp"

                    rows math.ceil(len(galleryList) / 3.0)

                    if len(galleryList) > 3:
                        cols 3
                    else:
                        cols len(galleryList)

                    spacing 25
                    mousewheel True

                    xalign 0.5
                    yalign 0.5

                    for name, gl in galleryList.items():
                        vbox:
                            if gl.unlocked:
                                imagebutton: 
                                    idle gl.small_size
                                    action [SetVariable("current_img_name", name), ShowMenu("preview"), With(Dissolve(0.5))]
                                text "[name]": 
                                    xalign 0.5
                                    color "#555"
                                    outlines []
                                    size 14
                            else:
                                imagebutton: 
                                    idle "mod_assets/mod_extra_images/galleryLock.png"
                                    action Show("dialog", message="This image is locked. Continue playing [config.name] to unlock this image.", ok_action=Hide("dialog"))
                                text "Locked": 
                                    xalign 0.5
                                    color "#555"
                                    outlines []
                                    size 14

                vbar value YScrollValue("gvp") xalign 0.99 ysize 560

    ## Gallery Screen #################################################################
    ##
    ## This screen shows the currently selected screen to the player in-game.
    screen preview():

        tag menu

        hbox: 
            add galleryList[current_img_name].image yoffset 40
        hbox:
            add Solid("#fcf") size(config.screen_width, 40)

        hbox:
            ypos 0.005
            xalign 0.5 
            text current_img_name: 
                color "#000"
                outlines[]
                size 24 

        hbox:
            ypos 0.005
            xalign 0.98
            if galleryList[current_img_name].artist:
                textbutton "?":
                    text_style "navigation_button_text"
                    action Show("dialog", message="Artist: " + galleryList[current_img_name].artist, ok_action=Hide("dialog"))

            textbutton "E":
                text_style "navigation_button_text"
                action Function(galleryList[current_img_name].export) 

            textbutton "X":
                text_style "navigation_button_text"
                action ShowMenu("gallery")

        textbutton "<":
            text_style "navigation_button_text"
            xalign 0.0
            yalign 0.5
            action Function(next_image, True)

        textbutton ">":
            text_style "navigation_button_text"
            xalign 1.0
            yalign 0.5
            action Function(next_image)

        on "replaced" action With(Dissolve(0.5))

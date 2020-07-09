![Readme Banner of Example Images](https://raw.githubusercontent.com/colinrsmall/ehm_faces/master/readme_banner.png)
*These hockey players do not exist.*
---
*This is not intended to be a how-to. If you are looking for a tutorial on how to train your own versions of StyleGAN, I would point you towards Gwern's page [here](https://www.gwern.net/Faces).*

---
# ehm_faces
EHM_Faces is a machine learning project that can generate high-quality, realistic ice hockey player portraits. Primarily meant for the game [Eastside Hockey Manager](http://www.eastsidehockey.com/) (EHM), this project can generate portraits either one-at-a-time or in batches (the resulting batches are called facepacks).

This project was started out of frustration over the relative difficulty and time-intensity of creating quality facepacks for EHM. While many content creators have poured hours into curating [high-quality facepacks](https://steamcommunity.com/workshop/browse/?appid=301120&searchtext=&childpublishedfileid=0&browsesort=trend&section=readytouseitems&requiredtags%5B%5D=Player+Facepack) for leagues such as the NHL, SHL, and KHL, there is a distinct lack of facepacks for smaller international and domestic leagues. This project is able to generate an infinite number of distinct player portraits, allowing us to generate fictional facepacks for these smaller leagues.

![Image showing a player's profile without a face compared to one with a generated face.](https://raw.githubusercontent.com/colinrsmall/ehm_faces/master/face_to_no_face.png)

# How It's Made
---
## Face Generator
The face generator uses a custom-trained [StyleGAN](https://github.com/NVlabs/stylegan) model to generate novel faces. As the name implies, StyleGAN is a [generative adverserial network](https://en.wikipedia.org/wiki/Generative_adversarial_network) built specifically for image synthesis. Commonly used for generating [images of fake people](https://thispersondoesnotexist.com/), this model can be easily retrained to generate images of hockey players.

#### Image Collection
As any good machine learning enthusiast will know, a model is only as good as the data it is trained on. Thankfully, the afformentioned community-created facepacks provided me the perfect set of pre-cropped, high-quality portraits from which I could train the model on. From combining several of the most popular facepacks available for EHM, over 15,000 raw images were available for training.

#### Image Cleaning/Preparation
However, these 15,000 images could not be used for training as they were right out of the facepacks. Some images were too grainy, some images' colors were messy, and some images were portraits of team staff, rather than players. It was important to first filter these images out, as the face generator model would have learned to recreate these lower-quality faces. The majority of this filtering was accomplished by filter images by their players's/staff's age. (The portraits inside the facepacks are designed to be read by the game, thus each image's filename contained the birthdate of the associated person as the game uses this to match the external portraits to internal players. Filtering, then, was esily accomplished by batch-processing the images based on their filename.) Images of older players and staff members accounted for the majority of these lower-quality images, so I filtered out any image whose associated person was older than 43 (the age of the oldest active NHL player). The remaining faces were then inspected manually, and any face deemed to be of too low quality was removed from the set.

Once lower-quality images were removed from the training set, faces with non-transparent backgrounds needed to be filtered out. Since I wanted the generator to learn the faces of the players without worrying about generating a background, I needed to use faces that had already been cropped-out from their background (thus leaving their background transparent). Thankfully, many of the faces included in the facepacks I used to collect training images had already been cropped-out. I used [ImageMagick](https://www.google.com/search?q=imagemagick&oq=imagemag&aqs=chrome.0.0l4j69i57j0l3.2327j0j7&sourceid=chrome&ie=UTF-8) to identify portraits without an alpha channel, indicating that they did not have a transparent background. Some images were not transparent yet had an alpha channel, thus the images once again needed to be inspected manually to remove any straggling non-transparent images.

However, StyleGAN does not support the generation of images with an alpha channel, so a uniform opaque background needed to be added to each image. A neutral blue color sampled from the user-interface of the game was chosen, as any background color left over after cropping out generated images with either Photoshop or the eventual face-cropper tool (as can be seen as the blue outline around the banner imagers) would seemlessly blend into the user-interface, becoming invisible to the player. (Originally, I chose a high-contrast pink color for the background, hoping that image editors or the eventual face-cropper tool would have an easier time distinguishing the head and shoulders of a face from a glaringly pink background. After some testing, this proved not to be the case as the leftover pink border around players was too glaring when placed against a blue background. This lead to me realize that I could re-train the generator with blue backgrounds and not have to worry about leftover background from final cropping.)

Once all images had had a background added, they needed to be resized to uniform dimensions. The majority of faces at this stage were of size 157px x 200px. The version of StyleGAN the generator was trained on requires square images of resolutions of a power of two, so the first step in getting images to the correct size was to expand their background out to 200px x 200px. Some images needed to be resized down, but the aspect ratio of the underlying image was kept the same in order to prevent distortion/stretching of the face.

The second step in resizing the images was to upscale them to 1024px x 1024px. This was accomplished with the wonderful (and wonderfuly-named) [Waifu2x project](https://github.com/nagadomi/waifu2x). I do all of my development on a MacBook pro in MacOS, so I was unable to take advantage of the GPU-accelerated original version of Waifu2x. I instead had to use [a C++ port of the project](https://github.com/DeadSix27/waifu2x-converter-cpp). Running this through all images took several days and nights of continuous upscaling.

The last step in preparing the image set was to use the [dataset_tool.py script](https://github.com/NVlabs/stylegan/blob/master/dataset_tool.py) provided in the StyleGAN repository to package the images into .tfrecords files compatible with StyleGAN.

#### StyleGAN Training

With the prepared .tfrecord image sets, it was finally time to train the StyleGAN model. The model itself was traing using Google Colab, with the notebook available [here](https://colab.research.google.com/drive/1NH7bvTj-G-_Ji4XJV0mowRGwl5mrd0bV?usp=sharing). This notebook is a heavily-edited version of [this notebook](https://github.com/ak9250/stylegan-art/blob/master/styleganportraits.ipynb), developed to train StyleGAN on artwork. 

As you might see in that notebook, or elsewhere, training StyleGAN from scratch is incredibely time-intensive. NVIDIA reports that training of models on 1024px x 1024px images can take anywhere from 6 to 41 **days** depending on how many GPUs you have available (NVIDIA benchmarked these times with Tesla v100 GPUs, roughly equivalent to what is available on Colab). Needless to say, I did not spend 41 days training this model. 

If you've taken a look at the original StyleGAN repository, you'll see that the example images in the readme (and at thispersondoesnotexist.com) are generated images of peoples' faces with zoom levels and poses quite similar to those of the training images. These example faces were generated with StyleGAN models trained on the [FFHQ](https://github.com/NVlabs/ffhq-dataset) dataset, a large dataset of high quality 1024px x 1024px images of human faces. NVIDIA, thankfully, published a version of StyleGAN trained on the FFHQ dataset available from the StyleGAN repository.

Using [transfer learning](https://en.wikipedia.org/wiki/Transfer_learning), we can re-train this pre-trained model on our new image set. This vastly cut down the time required for training, as the pre-trained FFHQ model is already "aware" of the general structure of human portraits - it "knows" what eyes, noses, ears, hair, etc. look like. Some training is required, as the model needs to learn that no hockey players are babies, few (if any) players wear glasses, and that there aren't female hockey players in the leagues from which the training images were pulled (yet).

Still, training was relatively quick, taking roughly 12 hours on Google Colab to reach a point where it was generating images that I deemed to be of sufficient quality. The below image shows progress of the model, from a relatviely early point in training on the right to a later point on the left.

![Training progress showing results from tick one to tick two.](https://raw.githubusercontent.com/colinrsmall/ehm_faces/master/Training%20Progress.png)

## Face Cropper

The StyleGAN model is only able to output images with an opaque background, thus an automated tool was needed to cut out the faces of the images from their background. This was accomplished with [Deeplab](https://github.com/tensorflow/models/tree/master/research/deeplab), a TensorFlow model developed for semantic image segmentation (used for labeling parts of an image). In this application, I trained a version of Deeplab to label two parts to an image - the face and the background.

In the process of creating the training image set for the face generator, I was left with a set of images of uniform size with uniform color backgrounds, a perfect training set itself for Deeplab. 

Some masking was needed over the face of the images, as Deeplab requires fully-masked images to alongside the training images. Deeplab learns to segment images by comparing the contents of an image within one masked area with the contents of the same image within a different masked area. This masking was also accomplished with ImageMagick. ImageMagick was told to, for each image in the training set, select all pixels of the background color, inverse the selection (thus selecting the face in the image), and replace all pixels in the selecion with a new, uniform color.

By telling the Deeplab model that all pixels within the background-color mask were an image's background pixels and that all inside the face-colored mask were an image's face, Deeplab can learn to create these color masks on novel images.

We can then feed generated images into the face-cropper tool, creating color masks for these new images. With both the masks and the original images, we can crop out faces from their backgrounds. (Although as you can see from the banner image, the face-cropper tool needs further development to refine its selections, as it currrently overselects faces by a few-pixel border.)

## Final Tool

The culmination of this project was a final tool developed to generate, cut-out, and correctly name images based on the names and birthdates of players from EHM database file. This tool was originally intended for individual use by players of the games themselves. In an ideal world, a player would be able to load the final tool on their computer, feed it a save-game file from their game, and have the tool generate images for any players without one (as many players do use human-created facepacks). However, installing such a tool (and the associated drivers and tools required by StyleGAN) was deemed too technical to be accesible for a significant amount of EHM players. 

Still, this final tool was developed (as avaiable in the Final Tool directory of this project), and a tentative hosted version can be found at [this Google Colab notebook](https://colab.research.google.com/drive/18te6gZfn8NTptAkbuXEN7cj2SVSkHoTy?usp=sharing).

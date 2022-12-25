import json
import os
import argparse

def merge_coco_datasets(ds1, ds2):
    assert ds1["categories"][0]["name"] == ds2["categories"][0]["name"] and ds1["categories"][1]["name"] == ds2["categories"][1]["name"] 
    finalDict = {}
    finalDict["info"] = ds1["info"]
    finalDict["categories"] = ds1["categories"]
    finalDict["images"] = ds1["images"]
    finalDict["annotations"] = ds1["annotations"]
    
    offset = len(ds1["images"])

    for img_data in ds2["images"]:
        img_data["id"] += offset
        finalDict["images"].append(img_data)
    
    for img_annot in ds2["annotations"]:
        img_annot["image_id"] += offset
        finalDict["annotations"].append(img_annot)

    return finalDict

def convert_to_single_class(ds, className):
    ds["categories"] = [
        {
            "id": 1,
            "name": className
        }
    ]
    for img_annot in ds["annotations"]:
        img_annot["category_id"] = 1


def verify(ds):
    # print(ds[0])
    if "disk" not in ds['categories'][0]['name'].lower():
        return False
    
    if "cup" not in ds['categories'][1]['name'].lower():
        return False
    
    return True

def swap_categories(ds, noOfCategories):
    ds['categories'][0], ds['categories'][1] = ds['categories'][1], ds['categories'][0]
    ds['categories'][0]['id'] = (noOfCategories + 1) - ds['categories'][0]['id']
    ds['categories'][1]['id'] = (noOfCategories + 1) - ds['categories'][1]['id']
    for annotation in ds['annotations']:
        annotation["category_id"] = (noOfCategories + 1) - annotation["category_id"]

def search(arr, id):
    n = len(arr)
    res = []
    left = 0
    right = n - 1
    while right > left:
        mid = (right + left) // 2
        if arr[mid]['image_id'] == id:
            res.append(arr[mid])
            if (mid > 0) and arr[mid-1]['image_id'] == id:
                res.append(arr[mid-1])
            if (mid < n - 1) and arr[mid + 1]['image_id'] == id:
                res.append(arr[mid+1])
            break
        elif arr[mid]['image_id'] > id:
            right = mid - 1
        else:
            left = mid + 1
    return res

def merge(args):
    # Image id in the final merged annotations
    image_count = 1
    # Annotation id in the final merged annotations
    annotations_count = 0

    # Final image data array
    merged_images = []
    # Final annotation data array
    merged_annotations = []

    # Keeping track of processed images
    image_names = []

    for ds in args:
        if verify(ds) == False:
            print("Verify -- FALSE")
            swap_categories(ds, 2)
        else:
            print("Verify -- TRUE")

        images = ds['images']
        annotations = sorted(ds['annotations'], key=lambda obj:obj['image_id'])
        
        for image in images:
            if image['file_name'] in image_names:
                continue

            id = image['id']
            curr_annotations = search(annotations, id)
            if len(curr_annotations) != 2:
                continue
            image['id'] = image_count
            image_count += 1
            merged_images.append(image)
            for annot in curr_annotations:
                annot['id'] = annotations_count
                annotations_count += 1
                annot['image_id'] = image['id']
                merged_annotations.append(annot)

            # Adding the current processed image name
            image_names.append(image['file_name'])
    merged_ds = {
        "info": {
            "description": "glaucoma-cup-disk"
        },
        "categories": [
            {
                "id": 1,
                "name": "Optic Disk"
            },
            {
                "id": 2,
                "name": "Optic Cup"
            }
        ]
    }

    merged_ds["images"] = merged_images
    merged_ds["annotations"] = merged_annotations
    print(max(image_names, key=lambda name:(len(name), name)))
    return merged_ds
            
if __name__ == "__main__":
    # ds1 = None
    # with open("./dataset/glaucoma_annotations_coco2.json", "r") as file1:
    #     ds1 = json.load(file1)
    
    # ds2 = None
    # with open("./glaucoma_annotations_2nd and 3rd row images_2 class_coco.json", "r") as file2:
    #     ds2 = json.load(file2)

    # finalDict = merge_coco_datasets(ds1, ds2)
    # convert_to_single_class(finalDict, "EyeCup")
    # with open("./glaucoma_annotations_1st 2nd and 3rd row images_1 class_coco.json", "w") as file3:
    #     json.dump(finalDict, file3)

    parser = argparse.ArgumentParser(description="Program to merge multiple COCO annotation files into one.")
    parser.add_argument("--src", help="Directory of all the JSON files.", default="", required=True)
    parser.add_argument("--dest", help="Path where output JSON file will be generated.", default="./")
    args = parser.parse_args()
    
    src = args.src
    dest = args.dest
    # print(src,"\n",dest)
    if src == "":
        print("Please provide source path.")
        raise Exception()

    ds_list = []

    for file_name in os.listdir(src):
        if file_name[len(file_name)-4:].lower() != "json":
            continue

        with open(os.path.join(src, file_name), "r") as file:
            ds = json.load(file)
            ds_list.append(ds)
    
    print(len(ds_list))
    merged_ds = merge(ds_list)
    with open(os.path.join(dest, "./output_coco.json"), "w") as file:
        json.dump(merged_ds, file)
    

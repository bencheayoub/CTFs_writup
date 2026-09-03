# Black Hat CTF --- Who Am I

## Challenge

**Category:** Reverse Engineering\
**File:** `WhatAmI.dll`

The goal is to locate the image embedded inside the DLL. The image is
stored as a Windows resource rather than as a normal PNG/JPEG file.

------------------------------------------------------------------------

## 1. Open the DLL in Ghidra

Import `WhatAmI.dll` into Ghidra and let the analysis finish.

In the **Program Trees** panel on the left, you can see the PE sections:

``` text
Headers
.text
.rdata
.data
.pdata
.rsrc
.reloc
Debug Data
.tdb
```

The interesting section is:

``` text
.rsrc
```

This is the Windows **resource section**, where resources such as icons,
dialogs, strings, and bitmaps can be stored.

------------------------------------------------------------------------

## 2. Inspect `.rsrc`

Select `.rsrc`.

The resource section starts at:

``` text
0x180005000
```

The DLL has an image base of:

``` text
0x180000000
```

Therefore, the beginning of `.rsrc` is:

``` text
0x180000000 + 0x5000
= 0x180005000
```

At this address Ghidra shows an `IMAGE_RESOURCE_DIRECTORY`.

------------------------------------------------------------------------

## 3. Identify the bitmap resource

Windows assigns numeric resource types.

The important one here is:

``` text
2
```

Resource type `2` corresponds to:

``` text
RT_BITMAP
```

Following the resource directory leads to the bitmap resource and its
`IMAGE_RESOURCE_DATA_ENTRY`.

The data entry contains an RVA pointing to:

``` text
0x000050A0
```

Because PE resource addresses are stored as RVAs, convert it to a
virtual address by adding the image base:

``` text
Image Base: 0x180000000
RVA:        0x000050A0
────────────────────────
VA:         0x1800050A0
```

So the actual bitmap data begins at:

``` text
0x1800050A0
```

------------------------------------------------------------------------

## 4. Verify that this is really the image

Jump to the address in Ghidra:

``` text
G
```

and enter:

``` text
0x1800050A0
```

The bytes at this location begin with:

``` text
28 00 00 00
DF 01 00 00
4D 01 00 00
01 00
04 00
```

These are the fields of a Windows `BITMAPINFOHEADER`.

### Header interpretation

``` text
28 00 00 00  → Header size = 40 bytes
DF 01 00 00  → Width       = 479
4D 01 00 00  → Height      = 333
01 00         → Planes      = 1
04 00         → Bit depth   = 4
```

Therefore the resource is a:

``` text
479 × 333
4-bit
Windows bitmap (DIB)
```

This also explains why searching the binary for the usual BMP magic
bytes:

``` text
42 4D
```

(`BM`) does not find the image. A bitmap stored as a Windows resource is
commonly stored as a DIB without the normal `BITMAPFILEHEADER`.

------------------------------------------------------------------------

## 5. Extracting the image

There are two useful approaches.

### Method A --- Use a PE resource extractor

Because the image is an `RT_BITMAP` resource, a PE resource extraction
tool can extract it directly.

The resource is:

``` text
Type: Bitmap
Resource ID: 102
Language: 0x409
```

After extraction, the resulting bitmap can be opened with an image
viewer.

### Method B --- Extract from Ghidra

In Ghidra, navigate to:

``` text
1800050A0
```

The bitmap data starts there.

The resource data size is approximately:

``` text
0x13898
```

The bytes can be exported and reconstructed as a BMP by adding the
appropriate `BITMAPFILEHEADER` in front of the existing DIB data.

The existing data already contains the `BITMAPINFOHEADER`, color table,
and pixel data; the missing part is the normal BMP file header.

------------------------------------------------------------------------

## 6. Why `0x1800050A0`?

The address is not arbitrary.

The calculation is:

``` text
.rsrc RVA
    ↓
0x5000

Bitmap resource data RVA
    ↓
0x50A0

Image base
    ↓
0x180000000

Final virtual address
    ↓

0x180000000 + 0x50A0
= 0x1800050A0
```

So the important chain is:

``` text
PE
└── .rsrc
    └── IMAGE_RESOURCE_DIRECTORY
        └── RT_BITMAP (type 2)
            └── Resource ID 102
                └── Language 0x409
                    └── IMAGE_RESOURCE_DATA_ENTRY
                        └── RVA 0x50A0
                            └── 0x1800050A0
                                └── Bitmap data
```

------------------------------------------------------------------------

## Result

The hidden image is an **embedded Windows bitmap resource** located at:

``` text
0x1800050A0
```

with the following properties:

  Property                     Value
  ------------------ ---------------
  Resource type          `RT_BITMAP`
  Resource type ID               `2`
  Resource ID                  `102`
  Language                   `0x409`
  Width                        `479`
  Height                       `333`
  Bit depth                  `4-bit`
  Bitmap data VA       `0x1800050A0`


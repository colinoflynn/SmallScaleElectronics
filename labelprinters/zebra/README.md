# Zebra Label Printer Templates

*Updates eventually coming*

The following is some short notes on printing labels with our GTX430t (GX43-102410-000) label printer. This printed uses the nice Zebra ZPL format data. Unlike other printers (Brady) it is very well documented how to use this data format, you can get the ZPL docs from Zebra.

To simplify things, I use a template that inserts text into the ZPL file and sends it to the printer. This repo is some quick notes on
how I do that.

## Making Templates

The easiest thing to do is to make a template in the [Zebra Designer software](https://www.zebra.com/us/en/products/software/barcode-printers/zebralink/zebra-designer.html), the 'Essentials' verion is free.

After you are ready, print your label by saving the ZPL output file, which will be a `something.prn` file. If you open that file
you'll notice the text you put into the label. Replace that text with the placeholder format used by this script, which is
`${key}`. So for example if in Zebra Designer you put `key1` as the text, replace `key1` with `${key1}` in the `.prn` file. You
can put sample text in the designed & replace it with the key as well, they don't need to match (as this is all manual).

This `.prn` file is now ready for usage! Here is an example of a script file I made:


```
CT~~CD,~CC^~CT~
^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4~SD15^JUS^LRN^CI0^XZ
^XA
^MMT
^PW1200
^LL0900
^LS0
^FO300,64^GF${some_graphic}
^FT1100,141^A0R,75,74^FH\^FDSome Fixed String^FS
^FT800,51^A0R,42,40^FH\^FD${TESTSTRING1}^FS
^FT750,51^A0R,42,40^FH\^FD${TESTSTRING2}^FS
^FT950,49^A0R,42,40^FH\^FDBoard S/N: ${SN}^FS
^FT900,49^A0R,42,40^FH\^FDTest Date: ${date}^FS
^FT250,49^A0R,42,40^FH\^FD-----------------------^FS
^PQ1,0,1,Y^XZ
```

This has the following keys:

* `some_graphic`
* `TESTSTRING1`
* `TESTSTRING2`
* `SN`
* `date`

The graphic one is special as it will be replaced with a base-64 encoded graphic file. The others will just be simple string replacements.

## Using The Python

Here is a simple example of string replacements:

```

anotherthing = "blah"
something = "haha"
sn = 81892398123
date = "Feb 33th"

zpl_replace = {
    "TESTSTRING1":anotherthing.encode('ascii','ignore'),
    "TESTSTRING2":something.encode('ascii','ignore'),
    "SN":sn.encode('ascii','ignore'),
    "date":date_str.encode('ascii','ignore')
}

zpl = zebra_utils.zpl_from_template("example-template.prn", zpl_replace)

z = zebra_utils.Zebra()
z.print_label(zpl)
```

### Datamatrix Codes / Graphics

If you need to use the datamatrix or graphic replacements, you'll need to use the `create_datamatrix_field_string` or `create_image_field_string` to generate the base64 encoded data. Once you have the string it's simply inserted similar to
any other string.

E.g., for datamatrix:

```
dm = "[)>" + chr(30) + "06" + chr(29) + bc_pn_newae + chr(29) + bc_pn_mouser + chr(29) + \
    bc_quantity + chr(29) + chr(29) +  bc_date_code + chr(29) + bc_coo + chr(29) + bc_lot_code + chr(30) + chr(4)

dm_str = zebra_utils.create_datamatrix_field_string(dm, scale=3.0)
```

In this example `dm_str` would be simply inserted into the `zpl_replace` dictionary.

When designing labels with these graphics, you can use the same method of inserting some placeholder image. See the above
example for the expected format - normally just delete everything after `64^GF` on the graphics line, and insert the
placeholder key.

## Barcodes

The zebra format includes some barcode support (it does not include the required datamatrix format for ECIA compatable labels, hence
the graphics hack above for them).

But if you are using linear barcodes or supported 2D barcodes, the Zebra engine will render your text into the barcode. Again you
can just create a template in the Zebra SW, and insert the 'string' into the ZPL file. The zebra engine will render that into a 2D
barcode and print on your label.
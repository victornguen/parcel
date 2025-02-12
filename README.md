# Parcel - tool for p2p file sharing
Parcel is a tool for p2p file sharing. Built on top of the [Iroh](https://www.iroh.computer/) protocol, 
Parcel allows you to share files with other people without the need for a central server.

## Installation
Parcel is available on PyPI, so you can install it using pip:
```bash
pip install parcel_share
```

## Usage
To share a file, run the following command:
```bash
parcel share <file>
```

You will see a message like this:
```bash
🚀 Sharing data - keep this running until transfer completes!
🔑 Share this ticket:
blobacg2ymif[...]
````

To receive a file you'll need the ticket that was generated when the file was shared. Run the following command:
```bash
parcel receive <ticket> <output_path>
```
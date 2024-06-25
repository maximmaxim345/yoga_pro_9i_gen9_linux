FROM debian:bookworm

# Install necessary build tools and dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  pkg-config \
  wget \
  libtiff-dev \
  libxml2-dev \
  python3 \
  && rm -rf /var/lib/apt/lists/*

# Install SampleICC
WORKDIR /tmp
RUN wget http://downloads.sourceforge.net/sourceforge/sampleicc/sampleicc%20tar/SampleIcc-1.6.8/SampleICC-1.6.8.tar.gz \
  && tar xzf SampleICC-1.6.8.tar.gz \
  && cd SampleICC-1.6.8 \
  && ./configure --prefix=/usr \
  && make \
  && make install \
  && cd .. \
  && rm -rf SampleICC-1.6.8 SampleICC-1.6.8.tar.gz

# Install IccXML
RUN wget http://downloads.sourceforge.net/sourceforge/iccxml/IccXML-Src/IccXML-0.9.8/IccXML-0.9.8.tar.gz \
  && tar xzf IccXML-0.9.8.tar.gz \
  && cd IccXML-0.9.8 \
  && ./configure --prefix=/usr \
  && make \
  && make install \
  && cd .. \
  && rm -rf IccXML-0.9.8 IccXML-0.9.8.tar.gz

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set the working directory to /app
WORKDIR /app
RUN wget https://www.notebookcheck.com/uploads/tx_nbc2/LEN160_3_2K_cal.icm

COPY . /app

# VOLUME [ "/output" ]

# The command to run when the container starts
CMD ["python3", "main.py"]

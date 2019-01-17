FROM python:3.4
COPY . /app
WORKDIR /app
RUN pip install requests
RUN pip install pyyaml
CMD python Listingdata.py --SellerURL 18.236.81.99 --SellerName Bella --password Pass@123  &&  python Interestdata.py --buyerURL 18.236.81.99 --buyerName Bella --password Pass@123
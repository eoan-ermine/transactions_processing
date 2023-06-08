CREATE TABLE "public.Client" (
	"identifier" VARCHAR(255) NOT NULL,
	CONSTRAINT "Client_pk" PRIMARY KEY ("identifier")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "public.Currency" (
	"code" CHAR(3) NOT NULL,
	CONSTRAINT "Currency_pk" PRIMARY KEY ("code")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "public.Transaction" (
	"id" serial NOT NULL,
	"client" VARCHAR(255) NOT NULL,
	"currency" CHAR(3) NOT NULL,
	"amount" double precision NOT NULL,
	"ruble_amount" double precision NOT NULL,
	CONSTRAINT "Transaction_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "public.UsualTransaction" (
	"id" serial NOT NULL,
	"transaction_id" serial NOT NULL,
	CONSTRAINT "UsualTransaction_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "public.BigTransaction" (
	"id" serial NOT NULL,
	"transaction_id" serial NOT NULL,
	CONSTRAINT "BigTransaction_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);


ALTER TABLE "public.Transaction" ADD CONSTRAINT "Transaction_fk0" FOREIGN KEY ("client") REFERENCES "public.Client"("identifier");
ALTER TABLE "public.Transaction" ADD CONSTRAINT "Transaction_fk1" FOREIGN KEY ("currency") REFERENCES "public.Currency"("code");

ALTER TABLE "public.UsualTransaction" ADD CONSTRAINT "UsualTransaction_fk0" FOREIGN KEY ("transaction_id") REFERENCES "public.Transaction"("id");

ALTER TABLE "public.BigTransaction" ADD CONSTRAINT "BigTransaction_fk0" FOREIGN KEY ("transaction_id") REFERENCES "public.Transaction"("id");

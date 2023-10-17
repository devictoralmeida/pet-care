from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView, Response, Request, status
from groups.models import Group

from pets.models import Pet
from pets.serializers import PetSerializer

from traits.models import Trait


class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        pets = Pet.objects.all()
        query_trait = request.query_params.get("trait", None)

        if query_trait:
            pets = Pet.objects.filter(traits__name__iexact=query_trait)

        result_pagination = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result_pagination, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.validated_data.pop("group")
        traits = serializer.validated_data.pop("traits")

        existent_group = Group.objects.get_or_create(group)

        pet = Pet.objects.create(
            **serializer.validated_data, group=existent_group[0]
        )

        for trait in traits:
            existent_traits = Trait.objects.filter(name__iexact=trait["name"])

            if existent_traits:
                pet.traits.add(existent_traits.first())
            else:
                existent_traits = Trait.objects.create(**trait)
                pet.traits.add(existent_traits)

        serializer = PetSerializer(pet)
        return Response(serializer.data, status.HTTP_201_CREATED)


class PetDetailView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, pk=pet_id)
        serializer = PetSerializer(pet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, pk=pet_id)
        serializer = PetSerializer(pet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop("group", None)
        traits = serializer.validated_data.pop("traits", None)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        if group:
            group_data, boolean = Group.objects.get_or_create(
                scientific_name=group["scientific_name"]
            )

            pet.group = group_data

        if traits:
            trait_list = []
            for trait in traits:
                trait_data, boolean = Trait.objects.get_or_create(
                    name__iexact=trait["name"]
                )
                trait_list.append(trait_data)
            pet.traits.set(trait_list)

        pet.save()
        serializer = PetSerializer(pet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, pk=pet_id)
        pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
